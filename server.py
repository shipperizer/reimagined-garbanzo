#!/usr/bin/env python

import logging
import sys
from os import environ
from time import sleep
import json

import pika


def init_logging():
    logger = logging.getLogger('server')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - [%(asctime)s] - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


logger = init_logging()


def mq_connection(blocking=True):
    credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbit'), environ.get('RABBITMQ_PASS', 'rabbit'))
    if blocking:
        return pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials))
    else:
        raise Exception('Only blocking is supported right now')


def registrator():
    logger.info(' [*] Waiting for clients. To exit press CTRL+C')
    connection = mq_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange='registrator', type='fanout')

    result = channel.queue_declare()
    queue_name = result.method.queue

    channel.queue_bind(exchange='registrator', queue=queue_name)


    def callback(ch, method, properties, body):
        logger.info('Registered client {}'.format(json.loads(body).get('client')))

    channel.basic_consume(callback, queue=queue_name, no_ack=True)

    channel.start_consuming()


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

        logger.info(" [x] Sent{0} #{1}".format(message, i))
        sleep(2)

    connection.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1:][0] == 'registrator':
        registrator()
    else:
        run()
