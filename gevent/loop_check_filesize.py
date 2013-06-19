#!/usr/bin/python
import os
import time
import fcntl

filelist = [{"Current_Load.rrd":1151496},{"Current_Users.rrd":384952},{"_HOST_.rrd":768224},{"HTTP.rrd":768224}]

while 1:
    for i in filelist:
        for filename,size in i.items():
            try:
                writen = 0
                fd = open(filename,'r')
                fcntl.flock(fd,fcntl.LOCK_SH)       
                while 1:
                    data = fd.read(8192)
                    if not data:
                        break
                    writen += len(data)
                if size != writen:
                    print "%s size incorrect!!!! %s" % (filename, writen)
                fcntl.flock(fd,fcntl.LOCK_UN)
                fd.close()
            except (OSError,IOError):
                pass
        time.sleep(1)
