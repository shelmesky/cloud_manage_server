#encoding: utf-8
############################################################################################
#                                                                                          #
# monitor path with inotify(python module), and send them to remote server.                #
# use sendfile(2) instead of send function in socket, if we have python-sendfile installed.#
# author: roy.lieu@gmail.com                                                               #
# vascloud@2012                                                                            #
#                                                                                          #
###########################################################################################
import gevent
import time
import os
import sys
import struct
import Queue
from gevent.coros import Semaphore
import fcntl
import signal
import logging
from gevent import socket
import errno


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

logger = logging.getLogger('Client')

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


def process_event(sync_server, queue, i):
    while 1:
        event = queue.get()
        if check_filetype(event.pathname):
            sock = socket.create_connection(sync_server)
            chunk_size = 1024
            filepath = event.path
            filename = event.name
            filesize = os.stat(event.pathname).st_size
            filepath_len = len(filepath)
            filename_len = len(filename)
                
            data = struct.pack("!LL128s128sL",filepath_len, filename_len, filepath,filename, filesize)
            fd = os.open(event.pathname, os.O_RDONLY|os.O_NONBLOCK)
            sock.send(data)
            
            print "start sync file: %s  size: %s" % (filename,filesize)
            

            sent_size = 0
            while 1:
                data = os.read(fd, chunk_size)
                if not data:
                    break
                try:
                    sent = sock.send(data)
                except socket.error, e:
                    if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                        raise
                    return
                sent_size += sent
                
            print "sent_size: %s" % sent_size
            
            if sent_size != filesize:
                logger.debug('read size %s small than filesize %s !!!!!!!!!!!!!!!\n' % (sent_size,filesize))
            os.close(fd)
            
            print "File %s size: %s\n" % (filename, filesize)
            sock.close()
        if debug:
            return
        #gevent.sleep(0)


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, events_queue):
        super(EventHandler,self).__init__()
        self.events_queue = events_queue
    
    def my_init(self):
        pass
    
    def process_IN_CLOSE_WRITE(self,event):
        self.events_queue.put(event)

    
def start_notify(path, mask, sync_server):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s: %(message)s',
                        )
    
    from gevent.queue import Queue
    events_queue = Queue()
    
    
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm,EventHandler(events_queue))
    wdd = wm.add_watch(path,mask,rec=False)
    notifier.start()
    
    if debug:
        import time
        start = time.time()
    lists = [gevent.spawn(process_event, sync_server, events_queue, i) for i in range(100)]
    
    gevent.joinall(lists)
    if debug:
        end = time.time()
        print end-start



def main():
    path = '/var/lib/pnp4nagios/perfdata/localhost'
    mask = pyinotify.IN_CLOSE_WRITE
    sync_server = ('127.0.0.1',9999)
    start_notify(path, mask, sync_server)


if __name__ == '__main__':
    main()


