# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq.consumer
    ~~~~~~~~~~~~~~~

    Usage :

    .. code-block:: python

       def some_task(message):
           return 'OK'

       from taskmq import Consumer
       consumer = Consumer('amqp.server.tld', 5672)
       exchange = consumer.exchange('exch', type='direct')
       basequeue = consumer.add_queue('basequeue')
       basequeue.register_task(some_task, basequeue)
       consumer.start()
"""
import logging
from .amqp import Connection
from .states import STARTED, FAILURE, SUCCESS


logger = logging.getLogger('tormq.consumer')


class Registry(object):
    """ """

    def __init__(self, consumer, queue):
        self.consumer = consumer
        self.queue = queue
        self.tasks = {}

    def __call__(self, message):
        """Call a task in registry

        :param message:  Incoming message object
        :type message:   Object Message
        """
        if not hasattr(message, 'body'):
            logger.info('Got an invalid message format, skip.')
            message.ack()
            return None

        body = message.body

        reply_exchange = body['reply_exchange']
        reply_key = body['reply_key']

        logger.info('Got a new task call, uid: %s', body['id'])

        # Task is not in registry.
        if not body['name'] in self.tasks.keys():
            logger.error('<Task "%s"> Does not exist in registry, skip.', body['id'])
            self.consumer.reply_state_failure(
                reply_exchange=reply_exchange,
                reply_key=reply_key,
                id=body['id'],
                reason="ConsumerError('cant find task in registry')"
            )
            message.ack()
            return None

        # Pass task to started state
        logger.info('<Task "%s"> Change state to STARTED', body['id'])
        if body['reply_states']:
            self.consumer.reply_state_started(
                reply_exchange=reply_exchange,
                reply_key=reply_key,
                id=body['id']
            )

        try:
            # Call the task.
            result = self.tasks[body['name']](*body['args'], **body['kwargs'])

        except Exception as reason:
            logging.error('<Task "%s"> Change state to FAILURE: %r', body['id'], reason)
            self.consumer.reply_state_failure(
                reply_exchange=reply_exchange,
                reply_key=reply_key,
                id=body['id'],
                reason=repr(reason)
            )

        else:
            logger.info('<Task "%s"> Change state to SUCCESS: %r', body['id'], result)
            self.consumer.reply_state_success(
                reply_exchange=reply_exchange,
                reply_key=reply_key,
                id=body['id'],
                result=result
            )

        finally:
            logger.debug('<Task "%s"> Acknowledge the message.', body['id'])
            message.ack()

    def register(self, fun, name=None):
        if not name:
            name = fun.__name__
        self.tasks[name] = fun

    def register(self, func=None, name=None):
        as_decorator = False

        def used_as_decorator():
            def wrapper(func):
                return func
            return wrapper
        if not func:
            func = used_as_decorator()
            as_decorator = True
        if not name:
            name = func.__name__
        self.tasks[name] = func
        return func if as_decorator else None


    def __repr__(self):
        return '<Queue Registry: {0}, {1} tasks>'.format(
            self.queue.name, len(self.tasks))


class Consumer(object):
    """
    An AMQP Consumer

    2 channels :
        Inbound  -> Incoming messages (task call)
        Outbound -> Outcoming message (task reply)
    """

    def __init__(self, host, port=None, vhost=None, user=None, password=None):
        """
        """
        # Connect to the broker.
        self.connection = Connection(
            host=host,
            port=port or 5672,
            userid=user or 'guest',
            password=password or 'guest',
            virtual_host=vhost or '/'
        )
        # Open two channels :
        #  -> inbound for incoming messages
        #  -> outbound for messages replies
        self.inbound_channel = self.connection.channel()
        self.outbound_channel = self.connection.channel()

    def reply_state_started(self, reply_exchange, reply_key, id):
        if not reply_exchange and not reply_key:
            return False
        message = {'id': id, 'state': STARTED}
        self.outbound_channel.publish(
            message,
            exchange=reply_exchange,
            routing_key=reply_key
        )
        return True

    def reply_state_success(self, reply_exchange, reply_key, id, result):
        if not reply_exchange and not reply_key:
            return False
        message = {'id': id, 'state': SUCCESS, 'result': result}
        self.outbound_channel.publish(
            message,
            exchange=reply_exchange,
            routing_key=reply_key
        )
        return True

    def reply_state_failure(self, reply_exchange, reply_key, id, reason):
        if not reply_exchange and not reply_key:
            return False
        message = {'id': id, 'state': FAILURE, 'reason': reason}
        self.outbound_channel.publish(
            message,
            exchange=reply_exchange,
            routing_key=reply_key
        )
        return True

    def exchange(self, name, mode='direct', passive=False, durable=False,
                 auto_delete=False, arguments=None, nowait=False):
        """
        Create Exchange
        """
        self.inbound_channel.declare_exchange(
            name=name,
            mode=mode,
            passive=False,
            durable=True,
            auto_delete=auto_delete,
            arguments=arguments,
            nowait=nowait
        )

    def queue(self, name):
        """
        Create a queue and is registry
        """
        # First create a queue
        queue = self.inbound_channel.declare_queue(name)

        # Create the registry for the queue
        registry = Registry(self, queue)

        # Prepare consuming queue with registry
        self.inbound_channel.consume(queue=queue, callback=registry)

        # Then, return the Registry object.
        return registry

    def start(self, timeout=None):
        while True:
            self.connection.drain_events(timeout)
