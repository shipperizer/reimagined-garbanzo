#!/usr/bin/env python

import logging
import sys
from os import environ
from time import sleep
import json
from uuid import uuid4

from celery import Celery
import pika


def init_logging():
    logger = logging.getLogger('server')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - [%(asctime)s] - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def init_celery():
    redis = environ.get('REDIS_HOST', 'localhost')

    app = Celery('server', broker='redis://{}:6379/2'.format(redis), backend='redis://{}:6379/3'.format(redis))

    @app.task
    def data():
        connection = mq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', type='fanout')

        message = json.dumps({'data': {'uuid': str(uuid4()), 'message': 'Payload incoming', 'type': 'data'}})
        channel.basic_publish(exchange='logs', routing_key='', body=message)
        logger.info("[x] Sent {0}".format(message))

    return app


logger = init_logging()
celery = init_celery()


def mq_connection(blocking=True):
    credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbit'), environ.get('RABBITMQ_PASS', 'rabbit'))
    ssl_opts = {'ca_certs': '/tmp/ca/cacert.pem', 'certfile': '/tmp/client/cert.pem', 'keyfile': '/tmp/client/key.pem'}
    if blocking:
        return pika.BlockingConnection(pika.ConnectionParameters(
            host=environ.get('RABBITMQ_HOST', 'localhost'), port=5671, credentials=credentials, ssl=True, ssl_options=ssl_opts)
        )
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
        if json.loads(body).get('type') == 'registration':
            logger.info('Registered client {}'.format(json.loads(body).get('client')))
        elif json.loads(body).get('type') == 'heartbeat':
            logger.info('Client {} alive'.format(json.loads(body).get('client')))
        else:
            logger.warning('Unknown message')

    channel.basic_consume(callback, queue=queue_name, no_ack=True)

    channel.start_consuming()


def run():
    connection = mq_connection()

    channel = connection.channel()

    channel.exchange_declare(exchange='logs',
                             type='fanout')

    for i in range(10000):
        message = json.dumps({'message': "Here's the server, over!"})
        channel.basic_publish(exchange='logs',
                              routing_key='',
                              body=message)

        logger.info("[x] Sent {0} #{1}".format(message, i))
        sleep(15)

    connection.close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1:][0] == 'registrator':
        registrator()
    else:
        run()
