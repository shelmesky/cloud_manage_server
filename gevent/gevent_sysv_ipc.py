#!/usr/bin/python
from gevent import monkey
monkey.patch_all()
import gevent
import sysv_ipc


mq = sysv_ipc.MessageQueue(89769810, max_message_size=4096)

def get_sysv(mq,i):
    while 1:
        for item in mq.receive():
            print "Greenthread %s got: " % i,item
            gevent.sleep(1)

greenthread_list = [gevent.spawn(get_sysv, mq,i) for i in xrange(10)]


print len(greenthread_list)

gevent.joinall(greenthread_list)
