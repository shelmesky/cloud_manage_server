#!/usr/bin/python
import time

files = 100
path = "/var/lib/pnp4nagios/perfdata/localhost/"


def bigcontent():
    content = ""
    for i in xrange(100000):
        content += str(i)+'byte'
    return content

while 1:
    for i in xrange(files):
        fd = open(path + str(i) + '.rrd','w')
        fd.write(bigcontent())
        fd.close()
    time.sleep(100)
