# -*- coding: utf-8 -*-
import logging
from taskmq import Consumer
from . import config


logging.basicConfig(level=logging.DEBUG)


def a_plus_b(a, b):
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError('Except an int type')
    return a + b


consumer = Consumer(
    host=config.BROKER_HOST,
    port=config.BROKER_PORT,
    user=config.BROKER_USER,
    password=config.BROKER_PASSWORD,
    vhost=config.BROKER_VHOST
)

print '...Create queue'
queue1 = consumer.queue('tests')
queue1.queue.purge()
print queue1

print '...Add task to the queue'
queue1.task(a_plus_b)
print queue1

consumer.start()
