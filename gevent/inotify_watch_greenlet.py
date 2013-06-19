#encoding: utf-8
############################################################################################
#                                                                                          #
# monitor path with inotify(python module), and send them to remote server.                #
# use sendfile(2) instead of send function in socket, if we have python-sendfile installed.#
# author: roy.lieu@gmail.com                                                               #
# vascloud@2012                                                                            #
#                                                                                          #
###########################################################################################
from gevent import monkey
import gevent
import time
import os
import sys
import struct
import threading
from gevent.queue import Queue
from gevent import socket
from gevent.coros import Semaphore
import fcntl


try:
    import pyinotify
except (ImportError, ImportWarnning):
    print "Hope this information can help you:"
    print "Can not find pyinotify module in sys path, just run [apt-get install python-pyinotify] in ubuntu."
    sys.exit(1)

#try:
#    from sendfile import sendfile
#except (ImportError,ImportWarnning):
#    pass


debug = False
filetype_filter = [".rrd"]

def check_filetype(pathname):
    for suffix_name in filetype_filter:
        if pathname[-4:] == suffix_name:
            return True
    try:
        end_string = pathname.rsplit('.')[-1:][0]
        end_int = int(end_string)
    except:
        pass
    else:
        # means pathname endwith digit
        return False


def process_event(sockfd_list, queue, addr, i):
    semaphore = Semaphore()
    while 1:
        semaphore.acquire()
        sockfd = sockfd_list[i]
        event = queue.get()
        chunk_size = 1024
        if check_filetype(event.pathname):
            #print "Greenlet %s got item: %s" % (i, event)
            filepath = event.path
            filename = event.name
            filesize = os.stat(event.pathname).st_size
            filepath_len = len(filepath)
            filename_len = len(filename)
                
            data = struct.pack("!LL128s128sL",filepath_len, filename_len, filepath,filename,filesize)
            fd = open(event.pathname,'rb')
            fcntl.flock(fd,fcntl.LOCK_SH)
            sockfd.write(data)
            sockfd.flush()
            
            print "File %s size: %s" % (filename, filesize)
            print 11111111111111
            offset = 0
            writen_size = 0
            if "sendfile" in sys.modules:
                #print "use sendfile(2)"
                if filesize > chunk_size:
                    while 1:
                        sent = sendfile(sockfd.fileno(), fd.fileno(), offset, chunk_size)
                        if sent == 0:
                            break
                        offset += sent
                else:
                    sendfile(sockfd.fileno(), fd.fileno(), offset, filesize)
            else:
                #print 22222222222222222
                #if filesize > chunk_size:
                #    times = filesize / chunk_size
                #    first_part_size = times * chunk_size
                #    second_part_size = filesize % chunk_size
                #    print "times: %s  first_part_size:%s  second_part_size:%s" % (times,first_part_size,second_part_size)
                #    print 3333333333333333
                #    # print "use original send function"
                #    while 1:
                #        data = fd.read(chunk_size)
                #        writen_size += len(data)
                #        sockfd.write(data)
                #        sockfd.flush()
                #        if writen_size == first_part_size:
                #            break
                #    print "writen_size in first_par: %s" % writen_size
                #    print 44444444444444444
                #    if second_part_size:
                #        data = fd.read(second_part_size)
                #        writen_size += len(data)
                #        sockfd.write(data)
                #        sockfd.flush()
                #    
                #else:
                #    data = fd.read(filesize)
                #    sockfd.write(data)
                #    sockfd.flush()
                print 222222222222222222
                while 1:
                    data = fd.read(chunk_size)
                    if not data: break
                    sockfd.write(data)
                    sockfd.flush()
                    
            print '333333333333333333\n'
            fcntl.flock(fd,fcntl.LOCK_UN)
            fd.close()
        if debug:
            return
        semaphore.acquire()
        gevent.sleep(0)


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, events_queue):
        super(EventHandler,self).__init__()
        self.events_queue = events_queue
    
    def my_init(self):
        pass
    
    def process_IN_CLOSE_WRITE(self,event):
        self.events_queue.put(event)

###############

class Event(object):
    def __init__(self):
        pass
    
    def __setattr__(self,name,value):
        object.__setattr__(self,name,value)
#################

#events_queue = Queue.Queue()
events_queue = Queue()
    

def insert():
    while True:
        for i in range(5):
            event = Event()
            event.path = "/var/lib/pnp4nagios/perfdata/localhost/"
            event.name = str(i) + '.rrd'
            event.pathname = event.path + event.name
            events_queue.put(event)
        gevent.sleep(5)


def start_notify(path, mask, sync_server):
   
    sockfd_list = []
    for i in range(100):
        sock = socket.create_connection(sync_server)
        sock.setblocking(0)
        sockfd = sock.makefile()
        sockfd_list.append(sockfd)
    
    #wm = pyinotify.WatchManager()
    #notifier = pyinotify.ThreadedNotifier(wm,EventHandler(events_queue))
    #wdd = wm.add_watch(path,mask,rec=False)
    #notifier.start()
    
    if debug:
        import time
        start = time.time()
    insert_spawn = gevent.spawn(insert)
    lists = [gevent.spawn(process_event, sockfd_list, events_queue, sync_server, i) for i in range(100)]
    lists.append(insert_spawn)
    gevent.joinall(lists)
    if debug:
        end = time.time()
        print end-start



def main():
    path = '/var/lib/pnp4nagios/perfdata/localhost'
    mask = pyinotify.IN_CLOSE_WRITE
    sync_server = ('127.0.0.1',6666)
    start_notify(path, mask, sync_server)


if __name__ == '__main__':
    main()


