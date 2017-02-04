#!/usr/bin/env python

import logging
from os import environ

import pika

credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbitmq'), environ.get('RABBITMQ_PASS', 'rabbitmq'))

connection = pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs',
                   queue=queue_name)

logging.error(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    logging.error(" [x] {}".format(body))

channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
