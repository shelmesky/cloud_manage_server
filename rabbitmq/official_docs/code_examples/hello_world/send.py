#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(virtual_host="/",
        credentials=pika.PlainCredentials("guest","cloudopen"),
        host='172.16.0.207'))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"
connection.close()