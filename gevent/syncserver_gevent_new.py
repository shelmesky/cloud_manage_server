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
import gevent

logger = logging.getLogger('Server')


def handle_socket(sock, address):
    chunk_size = 1024
    head_packet_format = "!LL128s128sL"
    head_packet_size = struct.calcsize(head_packet_format)
    data = sock.recv(head_packet_size)
    filepath_len, filename_len, filepath,filename, filesize = struct.unpack(head_packet_format,data)
    filepath = filepath[:filepath_len]
    filename = filename[:filename_len]
    
    print "start sync file: %s  size: %s" % (filename,filesize)
    
    receive_size =0 
    fd = open(filename,'wb')
    writen_size = 0
    if filesize > chunk_size:
        times = filesize / chunk_size
        first_part_size = times * chunk_size
        second_part_size = filesize % chunk_size
        #receive first part packets
        while 1:
            data = sock.recv(chunk_size)
            while len(data) < chunk_size:
                data += sock.recv(chunk_size - len(data))
            receive_size += len(data)
            if not data: break
            fd.write(data)
            fd.flush()
            if receive_size == first_part_size:
                break
            
        data = sock.recv(second_part_size)
        while len(data) < second_part_size:
                data += sock.recv(second_part_size - len(data))
        receive_size += len(data)
        fd.write(data)
        fd.flush()
        
        print "receive_size: %s" % receive_size
    else:
        data = sock.recv(filesize)
        while len(data) < filesize:
                data += sock.recv(filesize - len(data))
        fd.write(data)
        fd.flush()
        receive_size += len(data)
        
        print "receive_size: %s" % receive_size
        
    print "File %s size: %s\n" % (filename, receive_size)
    fd.close()
    sock.close()


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s: %(message)s',
                        )
    server = StreamServer(('0.0.0.0', 9999), handle_socket)
    print "SyncServer listend on tcp:9999"
    server.serve_forever()
    

if __name__ == '__main__':
    main()
