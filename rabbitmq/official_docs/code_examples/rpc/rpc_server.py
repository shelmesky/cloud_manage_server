#!/usr/bin/env python
import pika
import simplejson
import threading

class RpcServer(threading.Thread):
        def __init__(self, rabbitmq_server, username, password, virtual_host=None):
                super(RpcServer,self).__init__()
                if virtual_host == None:
                        virtual_host = "/"
                frame_max_size = 131072
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host=virtual_host,
                        credentials=pika.PlainCredentials(username,password),frame_max=frame_max_size,
                        host=rabbitmq_server))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue='rpc_queue')
        
        def run(self):
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(self.on_request, queue='rpc_queue')
                print " [x] Awaiting RPC requests"
                self.channel.start_consuming()       

        def on_request(self, ch, method, props, body):
            body = simplejson.loads(body)
            if body['head'] == 'update':
                response = "info is %s"  % (body,)
            else:
                response = body
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                             body=simplejson.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == '__main__':
        rabbitmq_server = "172.16.0.207"
        username = "guest"
        password = "cloudopen"
        server = RpcServer(rabbitmq_server,username,password)
        server.start()

