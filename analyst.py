#coding: utf-8
#!/usr/bin/python
import shelve
from httpclient import http_client
from api.openstack.cloudmessage import send_sms
from utils import get_on_notification, save_one_notification
from settings import *


def analyst_notification_result(result,option):
    try:
        result = eval(result[0][0])
    except Exception,e:
        return None

    try:
        notification_state = eval(option['notification_state'])
    except Exception,e:
        return None
    
    bandwidth_usage_warnning = int(notification_state['bandwidth_usage_warnning'])*1024*1024
    bandwidth_usage_critical = int(notification_state['bandwidth_usage_critical'])*1024*1024
    cpu_usage_warnning = int(notification_state['cpu_warnning'])
    cpu_usage_critical = int(notification_state['cpu_critical'])
    disk_usage_warnning = int(notification_state['disk_usage_warnning'])
    disk_usage_critical = int(notification_state['disk_usage_critical'])
    
    
    disks = result['vir_disks']
    nics = result['vir_interfaces']
    cpu = int(result['cpu_usage'])
    
    notification_result = dict()
    notification_result['ip'] = eval(option['ipaddress'])[0]
    notification_result['uuid'] = option['uuid']
    
    
    # this part does not working properly, cause function blockInfo does not work properly...
    #for k,v in disks.items():
    #    disk_usage = int( (Decimal(v['allocation']) / Decimal(v['capacity'])) * 100)
    #    if disk_usage > disk_usage_warnning and disk_usage < disk_usage_critical:
    #        notification_result['disk_usage'] = 1
    #    if disk_usage <= disk_usage_warnning:
    #        notification_result['disk_usage'] = 0
    #    if disk_usage >= disk_usage_critical:
    #        notification_result['disk_usage'] = 2
    
    
    if cpu_usage_warnning and cpu_usage_critical:
        if cpu > cpu_usage_warnning and cpu < cpu_usage_critical:
            notification_result['cpu_usage'] = 1
        if cpu <= cpu_usage_warnning:
            notification_result['cpu_usage'] = 0
        if cpu >= cpu_usage_critical:
            notification_result['cpu_usage'] = 2
        notification_result['cpu_usage_real'] = cpu

    if bandwidth_usage_warnning and bandwidth_usage_critical:
        nics_rx_bytes_max = list()
        nics_tx_bytes_max = list()
        for k,v in nics.items():
            nics_rx_bytes_max.append(int(v['rx_bytes']))
            nics_tx_bytes_max.append(int(v['tx_bytes']))
        rx_bytes_max = max(nics_rx_bytes_max)
        tx_bytes_max = max(nics_tx_bytes_max)
        
        if (rx_bytes_max > bandwidth_usage_warnning and rx_bytes_max < bandwidth_usage_critical) or \
            (tx_bytes_max > bandwidth_usage_warnning and tx_bytes_max < bandwidth_usage_critical):
            notification_result['bandwidth_usage'] = 1
        if rx_bytes_max <= bandwidth_usage_warnning or tx_bytes_max <= bandwidth_usage_warnning:
            notification_result['bandwidth_usage'] = 0
        if rx_bytes_max >= bandwidth_usage_critical or tx_bytes_max >= bandwidth_usage_critical:
            notification_result['bandwidth_usage'] = 2
    # send notification to user, use http or sms
    send_notification(notification_result,'notification')
    # save last notification, used in next time
    save_one_notification(notification_result,'monitifaction')
    
    return notification_result



def send_notification(result,result_type):
    """
    process message from moniting and notification and send to sms or http.
    """
    # process for notification message
    if result_type == "notification":
        s_data = dict()
        failed_item = 0
        s_data['type'] = 'notification'
        s_data['notification_type'] = 0
        s_data['host_name'] = result['ip']
        s_data['uuid'] = result['uuid']
        for k,v in result.items():
            if k == "bandwidth_usage":
                s_data['service_description'] = "Bandwidth Usage"
                if v==0:
                    s_data['state'] = 0
                    s_data['output'] = "BANDWIDTH SUCCESS"
                elif v==1:
                    s_data['state'] = 1
                    s_data['output'] = "BANDWIDTH WARNNING"
                    failed_item += 1
                elif v==2:
                    s_data['state'] = 2
                    s_data['output'] = "BANDWIDTH CRITICAL"
                    failed_item += 1
                s_data['host_name'] = result['ip']
                do_send_http(s_data)
            if k == "cpu_usage":
                s_data['service_description'] = "CPU Usage"
                if v==0:
                    s_data['state'] = 0
                    s_data['output'] = "CPU USAGE SUCCESS"
                if v==1:
                    s_data['state'] = 1
                    s_data['output'] = "CPU WARNNING: %s" % result['cpu_usage_real']
                    failed_item +=1
                elif v==2:
                    s_data['state'] = 2
                    s_data['output'] = "CPU CRITICAL: %s" % result['cpu_usage_real']
                    failed_item += 1
                s_data['host_name'] = result['ip']
                s_data['from'] = 'daemon'
                # send http and sms notification to user
                do_send_http(s_data)
                #do_send_sms(s_data)

    # process for moniting message
    if result_type == "moniting":
        nlist = list()
        temp_list = list()
        failed_item = 0
        all_item = 0
        for k,v in result.items():
            if k != 'uuid':
                # if checking of all items faild(except arp)
                all_failed_item_ip = k
                for i,j in v.items():
                    if i == "arp":                     
                        s_data = dict()
                        s_data['host_name'] = k
                        s_data['service_description'] = "ARP Check"
                        if j==0:
                            s_data['state'] = 2
                            s_data['output'] = "ARP UNREACHABLE"
                            nlist.append(s_data)
                            # yes we do not calculate arp state, because it can not indicate the state of instance
                            # but we have show it for user...
                            #failed_item += 1
                        #all_item += 1
                    elif i == "ping":
                        s_data = dict()
                        s_data['host_name'] = k
                        s_data['service_description'] = "PING Check"
                        if j==0:
                            s_data['state'] = 2
                            s_data['output'] = "PING UNREACHABLE"
                            nlist.append(s_data)
                            failed_item += 1
                        all_item += 1
                    elif i == "tcp":
                        for m,n in j.items():
                            s_data = dict()
                            s_data['host_name'] = k
                            s_data['service_description'] = "TCP Port Check"
                            if n==0:
                                s_data['state'] = 2
                                s_data['output'] = "TCP %s UNREACHABLE" % m
                                nlist.append(s_data)
                                failed_item += 1
                            all_item += 1
                    elif i == "udp":
                        for m,n in j.items():
                            s_data = dict()
                            s_data['host_name'] = k
                            s_data['service_description'] = "UDP Port Check"
                            if n==0:
                                s_data['state'] = 2
                                s_data['output'] = "UDP %s UNREACHABLE" % m
                                nlist.append(s_data)
                                failed_item += 1
                            all_item += 1
                
        for i in nlist:
            i['uuid'] = result['uuid']
            i['type'] = 'notification'
            i['notification_type'] = 1
            i['from'] = 'daemon'
            temp_list.append(i)
        
        if failed_item < all_item:
            for i in temp_list:
                do_send_http(i)
        elif failed_item == all_item:
            data = "Host %s seems down, please fix it quickly." % all_failed_item_ip
            do_send_sms(data)


def do_send_http(content):
    # type: moniting
    if content['notification_type'] == 1:
        http_client(URL_POST_DATA,content)
    # type: notification
    elif content['notification_type'] == 0:
        # if state is success, ignore it.
        if content['state'] !=0:
            http_client(URL_POST_DATA,content)


