from gevent import monkey
monkey.patch_select()
import gevent
from gevent.queue import Queue, JoinableQueue
from gevent import socket
import sysv_ipc
import web
import time
import sys
import os

web.debug = False
db = web.database(dbn='mysql',host='localhost',db='cloud_monitor',user='root',pw='root')


try:
    from scapy.all import *
except ImportError:
    print "Can not import python-scapy..."
    sys.exit(1)

def check_arp(ip):
    ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),timeout=1,verbose=0)
    if ans:
        return True
    else:
        return False

def run_query():
    gevent.sleep(0)
    return db.select('cloud_config').list()

#queue = JoinableQueue()
queue = Queue()


def print_queue(queue,i):
    while 1:
        url = queue.get()
        try:
            #ip = socket.gethostbyname(url)
            result = check_arp(url)
            #result = run_query()
            print 'GreenLet:%s -> %s -> %s = %s -> %s' % (i,time.time(), url, result, id(gevent.getcurrent()))
        finally:
            #queue.task_done()
            pass


#url_list = ['google.com','g.cn','google.cn','sohu.com','126.com','163.com','cctv.com','rootk.com','qq.com','sina.com', \
#            "baidu.com","17173.com","oschina.net","freebsdchina.org"]

greenthread_list = [gevent.spawn(print_queue,queue,i) for i in xrange(100)]

print len(greenthread_list)
while 1:
    for j in range(1,245):
        queue.put('172.16.0.%s' % j)
    gevent.sleep(100)

#queue.join()


gevent.joinall(greenthread_list)





