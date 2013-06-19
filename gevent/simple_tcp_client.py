#!/usr/bin/python
import sys
from gevent import socket
import gevent
from gevent.queue import Queue

queue = Queue()

def check_filetype(pathname):
    return True

def client(queue, sockfd_list,i):
    while 1:
        item = queue.get()
        sockfd = sockfd_list[i]
        sockfd.write("%s from greenlet %s \r\n" % (item, i))
        sockfd.flush()
        gevent.sleep(0)

def process_event(sockfd_list, queue, addr, i):
    while 1:
        event = queue.get()
        chunk_size = 1024
        if check_filetype(event):
            sockfd = sockfd_list[i]
            #print "Greenlet %s got item: %s" % (i, event)
            filepath, filename = event
            pathname = filepath + '/' + filename
            filesize = os.stat(filepath + '/' + filename).st_size
            filepath_len = len(filepath)
            filename_len = len(filename)
            offset = 0
                
            data = struct.pack("!LL128s128sL",filepath_len, filename_len, filepath,filename,filesize)
            fd = open(pathname,'rb')
            sockfd.write(data)
            sockfd.flush()
            
            if "sendfile" in sys.modules:
                # print "use sendfile(2)"
                while 1:
                    sent = sendfile(sock.fileno(), fd.fileno(), offset, chunk_size)
                    if sent == 0:
                        break
                    offset += sent
            else:
                if filesize >= chunk_size:
                    # print "use original send function"
                    while 1:
                        data = fd.read(chunk_size)
                        if not data: break
                        sockfd.write(data)
                        sockfd.flush()
                else:
                    data = fd.read(filesize)
                    sockfd.write(data)
                    sockfd.flush()
            #sockfd.close()
            fd.close()
        gevent.sleep(0)

def addlist():
    while 1:
        for i in range(1000):
            queue.put(i)
        gevent.sleep(5)

def put_item():
    while 1:
        for i in range(1000):
            events_queue.put(("/var/lib/pnp4nagios/perfdata/localhost", str(i)+".rrd"))
        gevent.sleep(5)

def main(path, mask, sync_server):
    sockfd_list = []
    for i in range(1000):
        sock =socket.create_connection(('127.0.0.1',6000))
        sock.setblocking(0)
        sockfd = sock.makefile('rw')
        sockfd_list.append(sockfd)
    
    #lists = [gevent.spawn(client, queue, sockfd_list,i) for i in range(1000)]
    #add = gevent.spawn(addlist)
    #lists.append(add)
    #gevent.joinall(lists)

    lists = [gevent.spawn(process_event,sockfd_list, events_queue, sync_server, i) for i in range(1000)]
    put = gevent.spawn(put_item)
    lists.append(put)
    gevent.joinall(lists)


if __name__ == '__main__':
    path = '/var/lib/pnp4nagios/perfdata/localhost'
    mask = pyinotify.ALL_EVENTS
    sync_server = ('127.0.0.1',9999)
    start_notify(path,mask,sync_server)
    
