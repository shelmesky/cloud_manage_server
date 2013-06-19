#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host="/",
        credentials=pika.PlainCredentials("guest","cloudopen"),
        host='172.16.0.207'))
channel = connection.channel()

channel.queue_declare(queue='hello')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

channel.start_consuming()