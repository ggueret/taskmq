# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq.amqp
    ~~~~~~~~~~~

    Basic AMQP bindings from original librabbitmq library.

    This program use librabbitmq a fast AMQP library written in C.
    Some improvements here, by making method shortcuts and support
    pluggable serializers.

    TaskMQ is axed on simplicity, if you want more or less, just look
    at projects like `Celery<http://www.celeryproject.org/>`_ or
    `Kombu<https://kombu.readthedocs.org/>`_.

    An example task call representation, in JSON format :

    .. code-block:: json

       {
           'id': <integer>,
           'task': <string>,
           'args': <list>,
           'kwargs': <dict>,
           'reply_exchange': <string>,
           'reply_key': <string>,
           'reply_states': <list>,  # states to reply (reduce callback queue)
           'time': <float>
       }

    And his reply representation, also in JSON :

    .. code-block:: json

       {
           'id': <integer>,
           'state': <integer>,  # 1 pending, 2 started, 3 failure, 4 success
           'reason': <string>,  # If state is 3 (failure)
           'result': <string>,  # If state is 4 (success)
           'time': <float>
       }
"""
import librabbitmq

from time import time as get_timestamp
from .serializer import serialize


class Binding(object):
    pass


class Exchange(object):
    """
    Represent an AMQP exchange
    """

    channel = None
    name = None

    def __init__(self, channel, name, mode='direct', passive=False,
                 durable=False, auto_delete=False, arguments=None,
                 nowait=False, commit=True):
        """Create an AMQP Exchange an return this object representation

        :param channel:      An opened channel to use
        :param name:         Name of this exchange
        :param mode:         Type: direct/fanout/topic/headers
        :param passive:      ?
        :param durable:      Survive broker restart
        :param auto_delete:  Deleted when all queues have finished using it
        :param arguments:    These are broker-dependent
        :param nowait:       <tosee>

        :return:  An exchange object representation
        :raises:   Error?

        """
        self.channel = channel
        if commit:
            self.channel.exchange_declare(
                exchange=name,
                type=mode,
                passive=passive,
                durable=durable,
                auto_delete=auto_delete,
                arguments=arguments,
                nowait=nowait
            )
        self.name = name
        self.mode = mode
        self.passive = passive
        self.durable = durable
        self.auto_delete = auto_delete
        self.arguments = arguments
        self.nowait = nowait
        self.committed = True if commit else False

    def bind(self, queue, routing_key=None, arguments=None, nowait=False):
        """Bind a queue to this Exchange

        :param queue:        An instancied Queue object or a String type
        :param routing_key:  The routing key to this queue (no need if fanout)
        :param arguments:    Arguments for the AMQP bind declare
        :param nowait:       <coming, or not>

        :raises:  Original _librabbitmq.ChannelError
        :return:  None <for now>
        """
        if isinstance(queue, Queue):
            queue = queue.name

        # [to update: return object?]
        return self.channel.queue_bind(
            queue=queue,
            exchange=self.name,
            routing_key=routing_key or '',
            arguments=arguments,
            nowait=nowait
        )

    def delete(self, if_unused=False):
        """Remove the current exchange

        :param if_unused: Remove exchange only if it's unused
        """
        # <voir le retour>
        status = self.channel.exchange_delete(
            exchange=self.name,
            if_unused=if_unused
        )
        del self
        return None

    def __repr__(self):
        return '<Exchange "{0}">'.format(self.name)


class Queue(object):
    """
    Represent an original AMQP queue
    """

    def __init__(self, channel, name=None, passive=False, durable=True,
                 exclusive=False, auto_delete=False, arguments=None,
                 nowait=False, commit=True):
        """AMQP queue representation

        :param channel:      An opened channel to use
        :param name:         Name of this queue (if None, is generated)
        :param passive:      ?
        :param durable:      The queue will survive a broker restart
        :param exclusive:    Used by only one connection and the queue
                             will be deleted when that connection closes
        :param auto_delete:  Queue is deleted when last consumer unsubscribes
        :param arguments:    Some brokers use it to implement additional
                             features like message TTL
        :param nowait:       ?

        :type channel:   Object Channel
        :type name:      String
        """
        self.channel = channel
        if commit:
            declare = self.channel.queue_declare(
                queue=name or '',
                passive=passive,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments,
                nowait=nowait
            )
        self.name = name or declare[0]
        self.passive = passive
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.arguments = arguments
        self.nowait = nowait
        self.committed = True if commit else False

    def purge(self, nowait=False):
        """Remove all messages in queue

        :param nowait: Not implemented

        :return:  Number of removed messages
        :rtype:   Int
        """
        return self.channel.queue_purge(self.name, nowait)

    def bind(self, exchange, routing_key=None, arguments=None, nowait=False):
        """Bind the queue to an exchange

        :param exchange:     Exchange object to bind with
        :param routing_key:  Routing key for this binding
        :param arguments:    Arguments to pass with binding creation
        :param nowait:       Not implemented
        """
        if isinstance(exchange, Exchange):
            exchange = exchange.name

        return self.channel.queue_bind(
            queue=self.name,
            exchange=exchange,
            routing_key=routing_key or '',
            arguments=arguments,
            nowait=nowait
        )

    def unbind(self, exchange, routing_key=None, arguments=None, nowait=False):
        """Unbind the queue

        :param exchange:     Exchange object to unbind with
        :param routing_key:  Routing key for this unbinding
        :param arguments:    Arguments to pass with binding remove
        :param nowait:       Not implemented
        """
        if isinstance(exchange, Exchange):
            exchange = exchange.name

        return self.channel.queue_unbind(
            queue=self.name,
            exchange=exchange,
            routing_key=routing_key or '',
            arguments=arguments,
            nowait=nowait
        )

    def delete(self, if_unused=False, if_empty=False, nowait=False):
        """Remove the current queue

        :param if_unused:
        :param if_empty:
        :param nowait: Not implemented
        """
        # <voir le retour>
        return self.channel.queue_delete(
            queue=self.name,
            if_unsued=if_unused,
            if_empty=if_empty,
            nowait=nowait
        )

    def __repr__(self):
        return '<Queue "{0}">'.format(self.name)


class Message(librabbitmq.Message):
    """
    A basic AMQP Message
    """
    def __init__(self, channel, properties, delivery_info, body):
        self.channel = channel
        self.properties = properties
        self.delivery_info = delivery_info
        self.raw_body = body
        self.body = self.decode()

    def is_state(self):
        must_have = {'id': (str, int), 'state': (int), 'time': (float)}
        for key, value in must_have.iteritems():
            # Check for keys.
            if key not in self.body:
                return False
        return True

    def is_call(self):
        must_have = {'id': (str, int), 'task': (str), 'args': (list),
                     'kwargs': (dict), 'time': (float)}
        for key, value in must_have.iteritems():
            if key not in self.body:
                return False
        return True

    def decode(self):
        return serialize.decode(
            self.properties['content_type'],
            self.properties['content_encoding'],
            str(self.raw_body)
        )


class Channel(librabbitmq.Channel):

    Message = Message
    Queue = Queue
    Exchange = Exchange

    def consume(self, queue, consumer_tag=None, no_local=False, no_ack=False,
                exclusive=False, callback=None, arguments=None, nowait=False):
        """
        """
        if isinstance(queue, Queue):
            queue = queue.name

        return self.basic_consume(
            queue=queue or '',
            consumer_tag=consumer_tag,
            no_local=no_local,
            no_ack=no_ack,
            exclusive=exclusive,
            callback=callback,
            arguments=arguments,
            nowait=nowait
        )

    def publish(self, body, serializer=None, exchange=None,
                routing_key=None, mandatory=False, immediate=False,
                **properties):
        """Publish a Task formatted message

        :param body:         The body of the task message
        :param exchange:     Exchange to use, None if default
        :param routing_key:  Routing key for the message
        :param mandatory:    <tosee>
        :param immediate:    <tosee>
        :param properties:   Headers of the message
        """
        # Add the current time.
        body['time'] = get_timestamp()

        # Encode the message.
        content_type, content_encoding, content = serialize.encode(body)
        properties['content_type'] = content_type
        properties['content_encoding'] = content_encoding

        # Send the message Task.
        return self.basic_publish(
            body=content,
            exchange=exchange or '',
            routing_key=routing_key or '',
            mandatory=mandatory,
            immediate=immediate,
            **properties
        )

    def declare_exchange(self, name, mode='direct', passive=False,
                         durable=False, auto_delete=False, arguments=None,
                         nowait=False):
        """Create an AMQP Exchange an return this object representation

        :param name:         Name of this exchange
        :param mode:         Type of AMQP Exchange (direct/fanout/...)
        :param passive:      <tosee>
        :param durable:      Exchange is keeped on server crash
        :param auto_delete:  Delete exchange when work are done
        :param arguments:    Arguments to pass for AMQP
        :param nowait:       <tosee>

        :return:  Exchange representation
        :rtype:   Object Exchange
        :raise:   Error?

        """
        return Exchange(
            channel=self,
            name=name,
            mode=mode,
            passive=False,
            durable=durable,
            auto_delete=auto_delete,
            arguments=arguments,
            nowait=nowait
        )

    def declare_queue(self, name=None, passive=False, durable=True,
                      exclusive=False, auto_delete=False, arguments=None,
                      nowait=False):
        """Create an AMQP Queue an return this object representation

        :param name:         Name of this queue
        :param passive:      <tosee>
        :param durable:      Messages in queue are keeped on crash
        :param exclusive:    <tosee>
        :param auto_delete:  Delete queue when work are done
        :param arguments:    Arguments to pass on queue creation
        :param nowait:       <tosee>

        :return:  Queue representation
        :rtype:   Object Queue
        :raise:   Error?
        """
        return Queue(
            channel=self,
            name=name,
            passive=passive,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments,
            nowait=nowait
        )


class Connection(librabbitmq.Connection):

    Message = Message
    Channel = Channel


class AMQPMixin(object):

    connection = None
    channel = None

    def __init__(self, host, port, vhost='/', user='guest',
                 password='guest', lazy=False):
        """ """
        self.connection = Connection(
            host=host,
            port=port,
            userid=user,
            password=password,
            virtual_host=vhost,
            lazy=lazy
        )
        self.channel = self.connection.channel()

    def start(self, timeout=0.0):
        while True:
            self.connection.drain_events(timeout)
