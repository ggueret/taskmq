# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq.producer
    ~~~~~~~~~~~~~~~

    Call tasks.

    Usage:

    .. code-block:: python

       from taskmq import Producer
       producer = Producer('amqp.server.tld', 5672)
       producer.call(
           exchange='/'
           queue='somequeue',
           task='sometask',
           args=['a', 'b'],
           kwargs={'a': 1, 'b': 2}
       )


    Task representation in JSON :

    .. code-block:: json

       {
           'id': 1,
           'task': 'sometask',
           'args': ['a', 'b'],
           'kwargs': {'a': 1, 'b': 2},
           'reply_to': 'otherqueue',
           'timestamp': 1372454529
       }
"""
from uuid import uuid4
from .amqp import Connection
from pprint import pprint


class Config(dict):

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


class Producer(object):

    uid_generator = uuid4

    def __init__(self, host, port=None, vhost=None, user=None, password=None,
                 lazy=False):
        """
        """
        self.host = host
        self.port = port or 5672
        self.user = user or 'guest'
        self.password = password or 'guest'
        self.vhost = vhost or '/'
        self.lazy = None

        # Load the config
        self.config = Config()
        self.load_default_config()

        self.connection = None
        if not lazy:
            self.connect()

    def connect(self):
        if not self.connection:
            self.connection = Connection(
                host=self.host,
                port=self.port,
                userid=self.user,
                password=self.password,
                virtual_host=self.vhost
            )
            self.outbound_channel = self.connection.channel()

    def disconnect(self):
        if self.connection:
            self.outbound_channel.close()
            self.connection.close()
            self.outbound_channel = self.connection = None

    def load_default_config(self):
        """Load default settings"""
        self.config.update({
            'serializer': None,
            'reply_exchange': None,
            'reply_key': None,
            'exchange': None,
            'routing_key': None,
            'uid_generator': None  # A implementer.
        })

    def generate_uid(self):
        """Generate a unique identifier for the task message

        Work with uid_generator by calling it.
        """
        return str(uuid4())

    def call_task(self, task, id=None, args=None, kwargs=None, serializer=None,
                  exchange=None, routing_key=None, reply_exchange=None,
                  reply_key=None, reply_states=True):
        """Send a task call
        """
        # If custom values are specified, use it.
        # Else, use self.config values.
        exchange = exchange or self.config.exchange
        routing_key = routing_key or self.config.routing_key
        reply_exchange = reply_exchange or self.config.reply_exchange
        reply_key = reply_key or self.config.reply_key

        message = {
            'id': id or self.generate_uid(),
            'name': task,
            'args': args or [],
            'kwargs': kwargs or {},
            'reply_exchange': reply_exchange,
            'reply_key': reply_key,
            'reply_states': reply_states
        }
        self.outbound_channel.publish(
            body=message,
            serializer=serializer or self.config.serializer,
            exchage=exchange,
            routing_key=routing_key
        )

    def async_call(self, task, *args, **kwargs):
        """Send a simple task"""
        return self.call_task(task, args=args, kwargs=kwargs)

    def check_blocking_response(self, task):
        """
        Used for blocking call.
        """
        if task.body['id'] == self._blocking_call_id:
            self._blocking_call_reply = task
            task.ack()
            self._blocking_call_got_anwser = True

    def call(self, task, *args, **kwargs):
        """
        Blocking Task call.
        """
        if self.lazy:
            self.connect()

        # Open a callback queue dedicated to this task and consume it.
        callback_queue = self.outbound_channel.declare_queue(auto_delete=True)
        self.outbound_channel.consume(
            queue=callback_queue,
            callback=self.check_blocking_response
        )

        # Generate a unique id and store it.
        self._blocking_call_id = self.generate_uid()

        # Send task with a reply_to.
        self.call_task(
            task,
            id=self._blocking_call_id,
            args=args,
            kwargs=kwargs,
            reply_key=callback_queue.name,
            reply_states=False
        )

        self._blocking_call_got_anwser = False

        # Wait for awnser.
        while not self._blocking_call_got_anwser:
            self.connection.drain_events()

        self._blocking_call_got_anwser = None
        task_result = self._blocking_call_reply
        del self._blocking_call_reply
        return task_result
