import sys
import os

try:
    from scapy.all import *
except ImportError:
    print "Can not import python-scapy..."
    sys.exit(1)

def check_arp(ip):
    ans,unans=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),timeout=1,verbose=0)
    if ans:
        return True
    else:
        return False

if __name__ == '__main__':
    print check_arp(sys.argv[1])