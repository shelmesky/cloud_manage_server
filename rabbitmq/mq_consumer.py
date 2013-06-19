#!/usr/bin/python
from amqplib import client_0_8 as amqp
import threading

class consumer(threading.Thread):
    def __init__(self):
        super(consumer, self).__init__()
    
    def run(self):
        queue_name = "roy_test_queue"
        exchange_name = "roy_test_exchange"
        
        # connect to message queue server
        conn = amqp.Connection(host="172.16.0.207:5672",userid="guest",
                               password="cloudopen", virtual_host="/", insist=False)
        chan = conn.channel()
        
        # declare queue and exchange
        chan.queue_declare(queue=queue_name, durable=True,
                           exclusive = False, auto_delete=False)
        chan.exchange_declare(exchange=exchange_name, type="direct",
                              durable=True, auto_delete=False)
        
        # bind queue to exchange
        chan.queue_bind(queue=queue_name,exchange=exchange_name,routing_key="roy")
        
        # callback function, called when message receieved.
        def recv_callback(msg):
            print 'Received: ' + msg.body
        
        # registed as consumer
        chan.basic_consume(queue = queue_name, no_ack=True,
                           callback=recv_callback, consumer_tag = "test_tag")
        
         
        while 1:
            chan.wait()
        
        chan.basic_cancel("test_tag")

consumer_thread = consumer()
consumer_thread.start()
