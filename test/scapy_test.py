import pcapy
import threading
import Queue
import os

queue = Queue.Queue()


def print_data():
    while 1:
        item = queue.get(True)
        print item

def process_incoming_pkts(hdr,data):
    queue.put((hdr,data))


def init_pcapy(dev):
        p = pcapy.open_live(dev, 1500, 0, 100)
        p.setfilter('icmp')
        (p.loop(-1, process_incoming_pkts))


devs = list()

for i in pcapy.findalldevs():
    if i not in ('any','\Device\NPF_GenericDialupAdapter'):
        devs.append(i)
        

for dev in devs:
    ti = threading.Thread(target=init_pcapy,args=(dev,))
    ti.daemon = False
    ti.start()

tp = threading.Thread(target=print_data,args=())
tp.daemon = False

tp.start()

