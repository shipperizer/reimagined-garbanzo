#!/usr/bin/env python

import logging
from os import environ
from uuid import uuid4, UUID
from pathlib import Path
import json

import pika


def get_key(file='.uuid'):
    uuid = Path(file)
    if uuid.exists() and uuid.is_file():
        logging.warning('Key file found')
        with open(file, 'r') as f:
            return UUID(f.read())
    else:
        logging.warning('Key file not found...creating one...')
        key = uuid4()
        with open(file, 'w') as f:
            f.write(str(key))
        return key


def mq_connection(blocking=True):
    credentials = pika.PlainCredentials(environ.get('RABBITMQ_USER', 'rabbitmq'), environ.get('RABBITMQ_PASS', 'rabbitmq'))
    if blocking:
        return pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RABBITMQ_HOST', 'localhost'), credentials=credentials))
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
            json.dumps({'client': str(key)}),
            pika.BasicProperties(content_type='application/json', delivery_mode=2),
            immediate=True
        )
        logging.info('Registering with key {}'.format(key))
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

    logging.info(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        logging.info(" [x] {}".format(body))

    channel.basic_consume(callback, queue=queue_name, no_ack=True)

    channel.start_consuming()


if __name__ == '__main__':
    register()
    run()
