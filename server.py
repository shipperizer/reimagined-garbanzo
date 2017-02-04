#!/usr/bin/env python

import logging
import sys
from os import environ
from time import sleep
import json

import pika


def mq_connection(blocking=True):
    credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbit'), environ.get('RABBITMQ_PASS', 'rabbit'))
    if blocking:
        return pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials))
    else:
        raise Exception('Only blocking is supported right now')


def registrator():
    connection = None
    try:
        logging.error(' [*] Waiting for clients. To exit press CTRL+C')
        connection = mq_connection()
        channel = connection.channel()

        channel.exchange_declare(exchange='registrator', type='fanout')

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='registrator', queue=queue_name)


        def callback(ch, method, properties, body):
            logging.info('Registered client {}'.format(json.loads(body).get('client')))

        channel.basic_consume(callback, queue=queue_name, no_ack=True)

        channel.start_consuming()
    finally:
        connection and connection.close()


def run():
    connection = mq_connection()

    channel = connection.channel()

    channel.exchange_declare(exchange='logs',
                             type='fanout')

    for i in range(10000):
        message = "Hello World!"
        channel.basic_publish(exchange='logs',
                              routing_key='',
                              body=message)

        logging.info(" [x] Sent{0} #{1}".format(message, i))
        sleep(2)

    connection.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1:][0] == 'registrator':
        registrator()
    else:
        run()
