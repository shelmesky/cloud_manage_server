#!/usr/bin/python
import pika
from pika.adapters import select_connection
import threading
import time
import uuid


#class Producer(threading.Thread):
class Consumer(object):
    def __init__(self,rabbitmq_server,username,password):
        self.rabbitmq_server = rabbitmq_server
        self.username = username
        self.password = password
        super(Consumer,self).__init__()
        self.parameters = pika.ConnectionParameters(virtual_host="/",
                credentials=pika.PlainCredentials(self.username,self.password),
                host=self.rabbitmq_server)
        self.queue_name = "dqueue_consumer"
        self.exchange_name = "dqueue"
        self.routing_key = "consumer"
        self.ready = False
    
    
    def run(self):
        select_connection.POLLER_TYPE="epoll"
        self.connection = select_connection.SelectConnection(parameters=self.parameters,
                                                on_open_callback=self.on_connected)
        self.connection.ioloop.start()
    
    
    def send_message(self,msg):
        self.corr_id = str(uuid.uuid4())
        self.properties = pika.BasicProperties(timestamp=time.time(),
                             app_id=self.__class__.__name__,
                             user_id=self.username,
                             content_type="text/plain",
                             correlation_id = self.corr_id,
                             reply_to = self.queue_name,
                             delivery_mode=1,
                             )
                            
        self.channel.basic_publish(exchange=self.exchange_name,
                      routing_key="producer",
                      body=msg,
                      properties=self.properties)
    
    
    def on_connected(self,connection):
        print "send: Connected to RabbitMQ"
        connection.channel(self.on_channel_open)
    
    
    def on_channel_open(self,channel_):
        global channel
        self.channel = channel_
        print "send: Received our channel"
        self.channel.queue_declare(queue=self.queue_name, durable=True,
                              exclusive=False, auto_delete=False,
                              callback=self.on_queue_declared)
        self.channel.exchange_declare(exchange=self.exchange_name, type="direct",
                              durable=True, auto_delete=False)
        self.channel.queue_bind(queue=self.queue_name,exchange=self.exchange_name,routing_key=self.routing_key) 
    
    
    def on_queue_declared(self,frame):
        print "send: Queue Declared"
        self.ready = True
        self.channel.basic_consume(self.handle_delivery,no_ack=True, queue=self.queue_name)
    
    
    def handle_delivery(self,ch, method, props, body):
        self.response = body
        print self.response
        self.send_message(self.response)


consumer = Consumer("127.0.0.1","guest","guest")
consumer.run()
#consumer.start()
#ret = consumer.send_message("123")
