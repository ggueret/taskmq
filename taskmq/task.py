# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!
"""

class Task(object):
    """
    """
    def __init__(self):
        # Task call related.
        self.id = None
        self.name = None
        self.args = None
        self.kwargs = None
        self.reply_exchange = None
        self.reply_key = None
        self.reply_states = None

        # Task state related.
        self.state = None
        self.reason = None
        self.result = None
        self.time = None
