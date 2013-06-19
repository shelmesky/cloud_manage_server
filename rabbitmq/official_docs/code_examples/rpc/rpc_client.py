#coding: utf-8
#!/usr/bin/env python
import pika
import uuid
import sys
import time
import simplejson
import threading


class RpcClient(threading.Thread):
    def __init__(self, rabbitmq_server, username, password, virtual_host=None):
        super(RpcClient,self).__init__()
        if virtual_host == None:
            virtual_host = "/"
        frame_max_size = 131072
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=virtual_host,
                credentials=pika.PlainCredentials(username,password), frame_max=frame_max_size,
                host=rabbitmq_server))

    
    def run(self):
        """
        declare queue and exchange and wait for incoming messages
        """
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True, durable=True,
                                            auto_delete=False)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    
    def call(self, head, msg):
        """
        send message to rpc queue and wait for response
        """
        message = dict()
        message['head'] = head
        message['body'] = msg
        message = simplejson.dumps(message)
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=message)
        while self.response is None:
            self.connection.process_data_events()
        return self.response


if __name__ == '__main__':
    rabbitmq_server = "127.0.0.1"
    username = "guest"
    password = "gust"
    client = RpcClient(rabbitmq_server,username,password)
    client.start()
    time.sleep(0.1)
    
    message = dict()
    print " [x] Requesting Message"
    response = client.call(sys.argv[1], sys.argv[2])
    print " [x] Got %s" % (response,)

