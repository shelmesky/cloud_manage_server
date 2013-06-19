#coding: utf-8
from gevent import monkey
monkey.patch_all()
from gevent.queue import JoinableQueue as Queue
from gevent.pool import Pool
import gevent
import shelve
import time
import simplejson
from api.scanner import arp_checker_gevent, icmp_checker_gevent, tcp_checker_gevent, udp_checker
from api.db import Instances, Session
from api.db_rawsql import raw_sql
from analyst_gevent import analyst_notification_result, send_notification
from utils import get_on_notification, save_one_notification


queue_moniting = Queue()
queue_notification = Queue()


def get_instance_config():
    """
    get configuration list for instance for checking.
    """
    while 1:
        #try:
        db = shelve.open('instances.dat','r')
        instances_config = db.items()[0][1]
        for i in instances_config:
            queue_moniting.put(i)
            queue_notification.put(i)
        #except:
        #    pass
        gevent.sleep(10)

def check_moniting_state(i):
    while 1:
        #try:
        session = Session()
        ins = queue_moniting.get(True)
        print "Greenlets %s got : %s" % (i,time.asctime()), " " , ins
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
                    instance_result[ip]['ping'] = 1 if icmp_checker_gevent.check_icmp(ip) == True else 0
                if arp:
                    instance_result[ip]['arp'] = 1 if arp_checker_gevent.check_arp(ip) == True else 0
                if tcp:
                    instance_result[ip]['tcp'] = dict()
                    if isinstance(tcp,unicode):
                        # if tcp is unicode string, means that's only one port.
                        port = tcp
                        instance_result[ip]['tcp'][port] = 1 if tcp_checker_gevent.check_tcp(ip,int(port)) == True else 0
                    else:
                        for port in tcp:
                            instance_result[ip]['tcp'][port] = 1 if tcp_checker_gevent.check_tcp(ip,int(port)) == True else 0
                #if udp:
                #    instance_result[ip]['udp'] = dict()
                #    if isinstance(udp,unicode):
                #        # if tcp is unicode string, means that's only one port.
                #        port = udp
                #        instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
                #    else:
                #        for port in udp:
                #            instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
        
        print "Greenlets %s got : %s" % (i,time.asctime()) , instance_result
        # send notification to user, use http or sms
        send_notification(instance_result,'moniting')
        # save last notification, used in next time
        save_one_notification(instance_result,'moniting')
        
        q = session.query(Instances).filter(Instances.uuid==ins['uuid'])
        if q.all():
            q.update(
                {Instances.moniting_state:simplejson.dumps(instance_result)}
            )
            session.commit()
        #except:
        #    pass


def check_moniting_state_icmp(i):
    while 1:
        #try:
        session = Session()
        ins = queue_moniting.get(True)
        print "Greenlets %s got : %s" % (i,time.asctime()), " " , ins
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
                    instance_result[ip]['ping'] = 1 if icmp_checker_gevent.check_icmp(ip) == True else 0
                #if arp:
                #    instance_result[ip]['arp'] = 1 if arp_checker_gevent.check_arp(ip) == True else 0
                #if tcp:
                #    instance_result[ip]['tcp'] = dict()
                #    if isinstance(tcp,unicode):
                #        # if tcp is unicode string, means that's only one port.
                #        port = tcp
                #        instance_result[ip]['tcp'][port] = 1 if tcp_checker_gevent.check_tcp(ip,int(port)) == True else 0
                #    else:
                #        for port in tcp:
                #            instance_result[ip]['tcp'][port] = 1 if tcp_checker_gevent.check_tcp(ip,int(port)) == True else 0
                ##if udp:
                #    instance_result[ip]['udp'] = dict()
                #    if isinstance(udp,unicode):
                #        # if tcp is unicode string, means that's only one port.
                #        port = udp
                #        instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
                #    else:
                #        for port in udp:
                #            instance_result[ip]['udp'][port] = 1 if udp_checker.checker_udp(ip,int(port)) == True else 0
        
        print "Greenlets moniting %s got : %s" % (i,time.asctime()) , instance_result
        # send notification to user, use http or sms
        send_notification(instance_result,'moniting')
        # save last notification, used in next time
        save_one_notification(instance_result,'moniting')
        
        q = session.query(Instances).filter(Instances.uuid==ins['uuid'])
        if q.all():
            q.update(
                {Instances.moniting_state:simplejson.dumps(instance_result)}
            )
            session.commit()
        #except:
        #    pass



def check_notification_state(i):
    while 1:
            session = Session()
            ins_opition = queue_notification.get(True)
            print "Greenlets %s got : %s" % (i,time.asctime()), " " , ins_opition
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
            print "Greenlets notification %s got : %s" % (i,time.asctime()) , ret
            if not ret:
                continue
            q = session.query(Instances).filter(Instances.uuid==ins_opition['uuid'])
            if q.all():
                q.update(
                    {Instances.notification_state:simplejson.dumps(ret)}
                )
                session.commit()



def run_network_and_system_check():
    spawn_publish_config = gevent.spawn(get_instance_config)
    
    #gevent.joinall([[spawn_publish_config],
    #    [gevent.spawn(check_moniting_state,i) for i in range(100)],
    #    [gevent.spawn(check_notification_state,i) for i in range(100)]
    #    ])
    
    
    


if __name__ == '__main__':
    run_network_and_system_check()
