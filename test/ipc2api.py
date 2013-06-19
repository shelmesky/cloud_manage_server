#!/usr/bin/python
#coding: utf-8
import sysv_ipc
import logging
import multiprocessing
from multiprocessing import Queue
import threading
from hashlib import md5
import time
import simplejson
import shelve

from settings import *

from instance import checker
from instance import checker_uuid
from api.db import Instances
from api.db import session
from scanner import run_network_and_system_check
from analyst import analyst_notification_result
from httpclient import http_client
from log import log
from inotify_watch import do_notify


class update_instances_to_db(threading.Thread):
    def __init__(self,queue):
        super(update_instances_to_db,self).__init__()
        self.daemon = False
        self.queue = queue
    
    def run(self):
        while 1:
            item = self.queue.get(True)
            for ins in item:
                q = session.query(Instances).filter(Instances.uuid==ins['id'])
                if not q.all():
                    i = Instances(ip_address=simplejson.dumps(ins['ip_address']), name=ins['name'], \
                                  uuid=ins['id'], state=ins['power_state'],physical_host=ins['physical_host'])
                    session.add(i)
                    session.commit()
                else:
                    q.update({Instances.ip_address:simplejson.dumps(ins['ip_address']),Instances.name:ins['name'], \
                              Instances.uuid:ins['id'],Instances.state:ins['power_state'],Instances.physical_host:ins['physical_host']
                    })
                    session.commit()


class post_notification_to_http(threading.Thread):
    """
    Check md5 message for notification and send it to remote server.
    """
    def __init__(self,queue):
        super(post_notification_to_http,self).__init__()
        self.queue = queue
        self.daemon = False

    def run(self):
        while 1:
            item = self.queue.get(True)
            s_data = dict()
            s_item = item.split('^')
            if s_item[0] == "notification":
                s_data['type'] = s_item[0]
                s_data['host_name'] = s_item[1]
                s_data['notification_type'] = s_item[2]
                s_data['output'] = s_item[3]
                s_data['reason_type'] = s_item[4]
                s_data['service_description'] = s_item[5]
                s_data['state'] = s_item[6]
                
                #check md5 signutare for "host_name + service_description + state"
                #to verify that remote api server has processed this message.
                md5_str = s_item[1] + s_item[5] + s_item[6]
                msg_md5 = md5(md5_str).hexdigest()
                return_code = self.check_md5(msg_md5)
                
                # return_code 2 and 1 will use in future
                if return_code == '2':
                    break
                elif return_code == '1':
                    break
                else:
                    url = URL_POST_DATA
                    data = s_data
                    http_client(url, data)
                
    def check_md5(self,msg):
        url = URL_CHECK_MD5
        data = {'data':msg}
        return http_client(url, data)


class get_msg_from_sysv_mq(multiprocessing.Process):
    """
    Get message from sysv ipc, and put it to FIFO queue.
    """
    def __init__(self,mq,nagios_queue):
        super(get_msg_from_sysv_mq,self).__init__()
        self.daemon = False
        self.mq = mq
        self.nagios_queue = nagios_queue
    
    def run(self):
        while 1:
            for line in self.mq.receive():
                if isinstance(line,str):
                    x= line.replace('\x00','')
                    self.nagios_queue.put(x)


class process_start_post_notification_to_http(multiprocessing.Process):
    """
    Process that used to lunch 200 threads for http post.
    """
    def __init__(self,queue):
        super(process_start_post_notification_to_http,self).__init__()
        self.daemon = False
        self.queue = queue
    
    def run(self):
        pool_POST = list()
        for i in range(200):
            pool_POST.append(post_notification_to_http(self.queue))
        for j in pool_POST:
            j.start()
        for k in pool_POST:
            k.join()


class check_nova_instances(multiprocessing.Process):
    def __init__(self,queue):
        super(check_nova_instances,self).__init__()
        self.deamon = False
        self.queue = queue
        self.logger = log(LOG_FILE)
    
    def run(self):
        while 1:
            #try:
            result = checker()
            self.queue.put(result)
            #except:
            #    pass
                #self.logger.error("Error happend while check instances.")
                #logger.exception(e)
            time.sleep(300)


class check_nova_instance_if_enable(threading.Thread):
    """
    Check instances in peorid time.
    """
    def __init__(self):
        super(check_nova_instance_if_enable,self).__init__()
        self.daemon = False
    
    def run(self):
        while 1:
            instances = session.query(Instances).all()
            for ins in instances:
                if not checker_uuid(ins.uuid):
                    session.query(Instances).filter(Instances.uuid==ins.uuid).delete()
                    session.commit()
            time.sleep(300)


class get_nova_instances_moniting_and_notification_config(threading.Thread):
    """
    Get configuration for instances from remote server.
    """
    def __init__(self):
        super(get_nova_instances_moniting_and_notification_config,self).__init__()
        self.daemon = False
        self.url = URL_GET_CONFIG
    
    def run(self):
        while 1:
            try:
                resp = http_client(self.url)
                try:
                    db = shelve.open('instances.dat','c')
                    db['data'] = eval(resp)
                finally:
                    db.close()
            except:
                pass
            time.sleep(300)


class process_start_update_instances_to_db(multiprocessing.Process):
    """
    Process that launch thread for update_instances_to_db.
    """
    def __init__(self,queue):
        super(process_start_update_instances_to_db,self).__init__()
        self.queue = queue
    
    def run(self):
        pool_update_instances = list()
        for i in range(200):
            pool_update_instances.append(update_instances_to_db(self.queue))
        for j in pool_update_instances:
            j.start()
        for k in pool_update_instances:
            k.join()


def main():

    # create a sysv ipc (message queue).
    mq = sysv_ipc.MessageQueue(KEY, max_message_size=MAX_MSG_SIZE)
    
    nagios_queue = Queue()
    instances_queue = Queue()
    
    
    # get message for nagios from sysv ipc message queue.
    queue_ipc = get_msg_from_sysv_mq(mq,nagios_queue)
    queue_ipc.start()
    
    
    # update notification from nagios to http server.
    http_q = list()
    for i in range(2):
        http_q.append(process_start_post_notification_to_http(nagios_queue))
    for j in http_q:
        j.start()
    
    
    #######################################
    # check nova instances and update all status to db
    tc = check_nova_instances(instances_queue)
    tc.start()
    
    tu = process_start_update_instances_to_db(instances_queue)
    tu.start()
    #######################################
    
    
    # periodic check instances from nova, make sure they are exists. 
    ti = check_nova_instance_if_enable()
    ti.start()
    
    
    # get moniting and notification config for instances
    tg = get_nova_instances_moniting_and_notification_config()
    tg.start()
    
    
    # run network and system check for instances.(get config from instances.dat)
    run_network_and_system_check()
    


if __name__ == '__main__':
    main()


