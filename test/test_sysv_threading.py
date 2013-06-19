#!/usr/bin/python
import threading
from Queue import Queue
import sysv_ipc

mq = sysv_ipc.MessageQueue(89769810, max_message_size=4096)

nagios_queue = Queue()

class get_msg_from_sysv_mq(threading.Thread):
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

class extract_queue(threading.Thread):
    def __init__(self,nagios_queue):
        super(extract_queue,self).__init__()
        self.queue = nagios_queue
    
    def run(self):
        while 1:
            item = self.queue.get()
            print item

t1 = get_msg_from_sysv_mq(mq,nagios_queue)
for i in range(100):
    t2 = extract_queue(nagios_queue)
    t2.start()

t1.start()
