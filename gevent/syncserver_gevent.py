#coding: utf-8
############################################################################################
#                                                                                          #
# listen on tcp port and handle client request on divided greenlet.                        #
# author: roy.lieu@gmail.com                                                               #
# vascloud@2012                                                                            #
#                                                                                          #
###########################################################################################
#/usr/bin/python
import logging
import sys
import struct
import fcntl
from gevent.server import StreamServer
from gevent import socket
import gevent
from gevent.coros import Semaphore

logger = logging.getLogger('handler')


def handle_socket(sock, address):
    semaphore = Semaphore()
    while 1:
        sock.setblocking(0)
        semaphore.acquire()
        sockfd = sock.makefile()
        chunk_size = 1024
        head_packet_format = "!LL128s128sL"
        head_packet_size = struct.calcsize(head_packet_format)
        data = sockfd.read(head_packet_size)
        if not data or len(data) != head_packet_size:
            return
        filepath_len, filename_len, filepath,filename, filesize = struct.unpack(head_packet_format,data)
        filepath = filepath[:filepath_len]
        filename = filename[:filename_len]
        #logger.debug("update file: %s" % filepath + '/' + filename)
        
        fd = open(filename,'wb')
        fcntl.flock(fd,fcntl.LOCK_EX)
        print "File %s size: %s" % (filename, filesize)
        print 111111111111111
        writen_size = 0
        if filesize > chunk_size:
            times = filesize / chunk_size
            first_part_size = times * chunk_size
            second_part_size = filesize % chunk_size
            print "times: %s  first_part_size:%s  second_part_size:%s" % (times,first_part_size,second_part_size)
            print 22222222222222222222
            #receive first part packets
            while 1:
                data = sockfd.read(chunk_size)
                fd.write(data)
                fd.flush()
                writen_size += len(data)
                if writen_size == first_part_size:
                    break
            print "writen_size in first_par: %s" % writen_size
            print 333333333333333333333
            if second_part_size:
                #receive the packet at last
                data = sockfd.read(second_part_size)
                fd.write(data)
                fd.flush()
                writen_size += len(data)
            print 4444444444444444444444
        else:
            data = sockfd.read(filesize)
            fd.write(data)
            fd.flush()
            writen_size += len(data)
            
        fcntl.flock(fd,fcntl.LOCK_UN)
        fd.close()
        print '555555555555555555555'
        print "File %s size: %s\n" % (filename, writen_size)
        semaphore.release()
        #logger.debug("File size: %s" % writen_size)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )
    try:
        server = StreamServer(('0.0.0.0', 6666), handle_socket)
        server.reuse_addr = 1
        print "SyncServer listend on tcp:9999"
        server.serve_forever()
    except KeyboardInterrupt:
        print "\nSyncServer quit now... byebye"
    

if __name__ == '__main__':
    main()
