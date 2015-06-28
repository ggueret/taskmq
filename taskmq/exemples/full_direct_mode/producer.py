# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!
"""
from taskmq import Producer

# Declare the producer.
producer = Producer(host='some.host.tld', user='user', password='', vhost='/')

# Configure the producer.
producer.config.serializer = 'json'
producer.config.reply_exchange = None
producer.config.reply_key = 'queue_1_replies'
producer.config.reply_state = None
producer.config.exchange = None
producer.config.routing_key = 'queue_1'


if __name__ == '__main__':

    # Call task using the default configuration.
    print producer.call('a_basic_task').__dict__

    # Call a task with customs parameters,
    # - publish on the second queue
    # - and ask reply on the second
    print producer.call(
        task='a_basic_task',
        routing_key='queue_2',
        reply_key='queue_2_replies'
    ).__dict__
