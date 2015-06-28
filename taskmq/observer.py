# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq.observer
    ~~~~~~~~~~~~~~~

    Observe tasks state an react.

    Usage:

    .. code-block:: python

       from django_taskmq import models
       def on_message(message):
           task_on_db = models.objects.get(id=message.id)
           task_on_db.state = message.state
           task_on_db.save()

       from taskmq import Observer
       observer = Observer('amqp.server.tld', 5672)
       observer.add_queue('callbacks', on_message)
       observer.start()
"""

from .amqp import Connection, Queue


class Observer(object):

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
        # Inbound for incoming messages
        self.inbound_channel = self.connection.channel()

    def queue(self, name, passive=False, durable=True, exclusive=False,
              auto_delete=False, arguments=None, nowait=False):
        """
        """
        return self.inbound_channel.declare_queue(
            name=name,
            passive=passive,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments,
            nowait=nowait
        )

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

    def watch(self, queue, func):
        self.inbound_channel.consume(queue=queue, callback=func)

    def start(self, timeout=None):
        while True:
            self.connection.drain_events(timeout)
