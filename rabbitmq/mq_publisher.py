from amqplib import client_0_8 as amqp
import sys

def file_msg():
    fd = open('/var/log/syslog','r')
    msg = fd.read()
    print len(msg)
    return msg

exchange_name = "roy_test_exchange"
routing_key = "roy"

conn = amqp.Connection(host="172.16.0.207:5672", userid="guest", password="cloudopen", virtual_host="/", insist=False)
chan = conn.channel()

msg = amqp.Message(sys.argv[1])
#msg = amqp.Message(file_msg())
msg.properties["delivery_mode"] = 2
chan.basic_publish(msg,exchange=exchange_name,routing_key=routing_key)

chan.close()
conn.close()