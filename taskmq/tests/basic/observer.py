# -*- coding: utf-8 -*-

from taskmq import Observer
from taskmq.states import states
from . import config


def on_reply(message):
    print 'Got a state reply', states[message.body['state']]
    message.ack()


observer = Observer(
    host=config.BROKER_HOST,
    port=config.BROKER_PORT,
    user=config.BROKER_USER,
    password=config.BROKER_PASSWORD,
    vhost=config.BROKER_VHOST
)

observer.watch('tests_replies', on_reply)
observer.start()
