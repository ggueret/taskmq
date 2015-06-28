# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!
"""
import logging
from taskmq import Consumer
from time import sleep

# Declare the consumer.
consumer = Consumer(host='some.host.tld', user='user', password='', vhost='/')

# Declare a direct exchange.
base_exchange = consumer.exchange('base_exchange')

# Declare two queues.
queue_1 = consumer.queue('queue_1')
queue_2 = consumer.queue('queue_2')


def a_basic_task():
    sleep(10)
    return 'HEY'

queue_1.register(a_basic_task)

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.stop()
