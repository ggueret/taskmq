# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!
"""
from taskmq import Observer

observer = Observer(host='some.host.tld', user='user', password='', vhost='/')

# Create the queue to observe.
queue_1 = observer.queue('queue_1_replies')
queue_2 = observer.queue('queue_2_replies')


def msg_on_queue_1(message):
    print message.body['state']
    print 'Got a message in the first queue...'
    message.ack()


def msg_on_queue_2(message):
    print message.body['state']
    print 'Got a message in the second queue...'
    message.ack()

observer.watch(queue_1, msg_on_queue_1)
observer.watch(queue_2, msg_on_queue_2)


if __name__ == '__main__':

    try:
        observer.start()

    except KeyboardInterrupt:
        observer.stop()
