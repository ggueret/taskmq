# -*- coding: utf-8 -*-
import random
from taskmq import Producer
from . import config


producer = Producer(
    host=config.BROKER_HOST,
    port=config.BROKER_PORT,
    user=config.BROKER_USER,
    password=config.BROKER_PASSWORD,
    vhost=config.BROKER_VHOST,
    reply_to='test_replies'
)

while True:
    print 'send operation'
    producer.call(
        queue='tests',
        task='a_plus_b',
        args=[random.randint(0, 9), random.randint(0, 9)]
    )
