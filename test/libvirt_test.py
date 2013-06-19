import libvirt as _libvirt
import time


class libvirt_client(object):
    def __init__(self,uri):
        self.ip = uri
        self.uri = 'qemu+tcp://root@%s/system' % uri
        self.connect()
    
    def connect(self):
        self.conn = _libvirt.open(self.uri)
    
    def check(self,uuid_string):
        result = dict()
        time_sleep = 3
        dom = self.conn.lookupByUUIDString(uuid_string)
        infos_first = dom.info()
        start_cputime = infos_first[4]
        start_time = time.time()
        time.sleep(time_sleep)
        infos_second = dom.info()
        end_cputime = infos_second[4]
        end_time = time.time()
        cputime = (end_cputime - start_cputime)
        cores = infos_second[3]
        cpu_usage = 100 * cputime / (time_sleep*cores*1000000000)
        print cpu_usage


virt = libvirt_client('172.16.0.209')
virt.check('ef809edd-2168-4007-8319-3d2acbc49aff')
