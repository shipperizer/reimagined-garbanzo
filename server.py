#!/usr/bin/env python
import sys
from os import environ

import pika

credentials = (environ.get('RABBITMQ_USER', 'rabbitmq'), environ.get('RABBITMQ_PASS', 'rabbitmq'),)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials)

channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)

print(" [x] Sent %r" % message)

connection.close()
