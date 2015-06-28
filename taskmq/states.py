# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq.states
    ~~~~~~~~~~~~~

    1 -> PENDING
    2 -> STARTED
    3 -> FAILURE
    4 -> SUCCESS
"""

__all__ = ['PENDING', 'STARTED', 'FAILURE', 'SUCCESS']

states = {
    1: 'PENDING',
    2: 'STARTED',
    3: 'FAILURE',
    4: 'SUCCESS'
}

PENDING = 1
STARTED = 2
FAILURE = 3
SUCCESS = 4
