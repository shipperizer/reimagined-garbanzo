#!/usr/bin/env python

import logging
from os import environ
from uuid import uuid4, UUID
from pathlib import Path
from datetime import timedelta
import json

from celery import Celery
from celery.schedules import crontab
import pika


def init_logging():
    logger = logging.getLogger('client')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] - [%(asctime)s] - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def init_celery():
    redis = environ.get('REDIS_HOST', 'localhost')

    app = Celery('client', broker='redis://{}:6379/0'.format(redis), backend='redis://{}:6379/1'.format(redis))

    @app.task
    def heartbeat():
        key = get_key()
        try:
            connection = mq_connection()
            channel = connection.channel()

            channel.basic_publish(
                'registrator',
                '',
                json.dumps({'client': str(key), 'type': 'heartbeat'}),
                pika.BasicProperties(content_type='application/json', delivery_mode=1)
            )

            logger.info('Heartbeat {}'.format(key))
        finally:
            connection and connection.close()

    app.conf.beat_schedule = {
        'heartbeat': {
            'task': 'client.heartbeat',
            'schedule': timedelta(seconds=60),
            'args': (),
        },
    }

    return app


logger = init_logging()
celery = init_celery()

def get_key(file='.uuid'):
    uuid = Path(file)
    if uuid.exists() and uuid.is_file():
        logger.warning('Key file found')
        with open(file, 'r') as f:
            return UUID(f.read())
    else:
        logger.warning('Key file not found...creating one...')
        key = uuid4()
        with open(file, 'w') as f:
            f.write(str(key))
        return key


def mq_connection(blocking=True):
    credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbit'), environ.get('RABBITMQ_PASS', 'rabbit'))
    ssl_opts = {'ca_certs': '/tmp/ca/cacert.pem', 'certfile': '/tmp/client/cert.pem', 'keyfile': '/tmp/client/key.pem'}
    if blocking:
        return pika.BlockingConnection(pika.ConnectionParameters(
            host=environ.get('RABBITMQ_HOST', 'localhost'), port=5671, credentials=credentials, ssl=True, ssl_options=ssl_opts)
        )
    else:
        raise Exception('Only blocking is supported right now')


def register():
    connection = None
    key = get_key()
    try:
        connection = mq_connection()
        channel = connection.channel()

        channel.basic_publish(
            'registrator',
            '',
            json.dumps({'client': str(key), 'type': 'registration'}),
            pika.BasicProperties(content_type='application/json', delivery_mode=1)
        )
        logger.info('Registering with key {}'.format(key))
    finally:
        connection and connection.close()


def run():
    connection = mq_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange='logs',
                             type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs',
                       queue=queue_name)

    logger.info(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        logger.info(" [x] {}".format(body))

    channel.basic_consume(callback, queue=queue_name, no_ack=True)

    channel.start_consuming()


if __name__ == '__main__':
    register()
    run()
