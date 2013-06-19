#coding: utf-8
#!/usr/bin/evn python

import shelve
import time
import threading
import Queue
import simplejson
from api.scanner import arp_checker, icmp_checker, tcp_checker, udp_checker
from api.db import Instances, Session
from api.db_rawsql import raw_sql
from analyst import analyst_notification_result, send_notification
from utils import get_on_notification, save_one_notification

from log import logger

queue_moniting = Queue.Queue()
queue_notification = Queue.Queue()


def get_instance_config():
    """
    get configuration list for instance for checking.
    """
    while 1:
        try:
            db = shelve.open('instances.dat','c')
            instances_config = db.items()[0][1]
            for i in instances_config:
                queue_moniting.put(i)
                queue_notification.put(i)
        except Exception,e:
                logger.exception(e)
        time.sleep(300)



class check_moniting_state(threading.Thread):
    """
    check moniting state for instance
    """
    def __init__(self):
        super(check_moniting_state,self).__init__()
        self.daemon = True
        self.session = Session()
        
    
    def run(self):
        while 1:
            #try:
            ins = queue_moniting.get(True)
            instance_result = dict()
            moniting_state = eval(ins['moniting_state'])
            ipaddress = eval(ins['ipaddress'])
            ping = moniting_state['ping']
            arp = moniting_state['arp']
            tcp = moniting_state['tcp']
            udp = moniting_state['udp']
            if ipaddress:
                instance_result['uuid'] = ins['uuid']
                for ip in ipaddress:
                    instance_result[ip] = dict()
                    if ping:
                        instance_result[ip]['ping'] = 1 if icmp_checker.check_icmp(ip) == True else 0
                    if arp:
                        instance_result[ip]['arp'] = 1 if arp_checker.check_arp(ip) == True else 0
                    if tcp:
                        instance_result[ip]['tcp'] = dict()
                        if isinstance(tcp,unicode):
                            # if tcp is unicode string, means that's only one port.
                            port = tcp
                            instance_result[ip]['tcp'][port] = 1 if tcp_checker.check_tcp(ip,int(port)) == True else 0
                        else:
                            for port in tcp:
                                instance_result[ip]['tcp'][port] = 1 if tcp_checker.check_tcp(ip,int(port)) == True else 0
                    if udp:
                        instance_result[ip]['udp'] = dict()
                        if isinstance(udp,unicode):
                            # if tcp is unicode string, means that's only one port.
                            port = udp
                            instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
                        else:
                            for port in udp:
                                instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
            # send notification to user, use http or sms
            send_notification(instance_result,'moniting')
            # save last notification, used in next time
            save_one_notification(instance_result,'moniting')
            
            q = self.session.query(Instances).filter(Instances.uuid==ins['uuid'])
            if q.all():
                q.update(
                    {Instances.moniting_state:simplejson.dumps(instance_result)}
                )
                self.session.commit()
            #except:
            #    pass
            
            # dont forget to close session at the end
            self.session.close()



class check_notification_state(threading.Thread):
    """
    check moniting state for instance
    """
    def __init__(self):
        super(check_notification_state,self).__init__()
        self.daemon = True
        self.session = Session()
        
    
    def run(self):
        while 1:
                ins_opition = queue_notification.get(True)
                sql = """
                    SELECT result
                    FROM cloud_result
                    WHERE TIME = (
                    SELECT MAX( TIME ) 
                    FROM cloud_result ) 
                    AND uuid
                    IN (
                    '%s'
                    )
                    """ % ins_opition['uuid']
                result = raw_sql(sql)
                # if result is empty, skip current loop.
                if not result:
                    continue
                # analyst notification in another function
                ret = analyst_notification_result(result,ins_opition)
                if not ret:
                    continue
                q = self.session.query(Instances).filter(Instances.uuid==ins_opition['uuid'])
                if q.all():
                    q.update(
                        {Instances.notification_state:simplejson.dumps(ret)}
                    )
                    self.session.commit()


def run_network_and_system_check():
    tc_pool = list()
    for i in range(50):
        tc_pool.append(check_moniting_state())
    for j in tc_pool:
        j.start()
    
    tm_pool = list()
    for l in range(50):
        tm_pool.append(check_notification_state())
    for m in tm_pool:
        m.start()
    
    tg = threading.Thread(target=get_instance_config,args=())
    tg.daemon = False
    tg.start()
    


if __name__ == '__main__':
    run_network_and_system_check()
