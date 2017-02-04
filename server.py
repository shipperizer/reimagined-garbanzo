#!/usr/bin/env python

import logging
import sys
from os import environ
from time import sleep

import pika

credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbitmq'), environ.get('RABBITMQ_PASS', 'rabbitmq'))

connection = pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials))

channel=connection.channel()

channel.exchange_declare(exchange='logs',
                         type='fanout')

for i in range(10000):
    message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    channel.basic_publish(exchange='logs',
                          routing_key='',
                          body=message)

    logging.error(" [x] Sent{0} #{1}".format(message, i))
    sleep(2)

connection.close()
