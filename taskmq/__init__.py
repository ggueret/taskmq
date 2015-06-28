# -*- coding: utf-8 -*-
"""
    !!! NOT READY FOR PRODUCTION !!!

    taskmq - remote procedure call throught AMQP
    Copyright (C) 2013  Geoffrey Gueret

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Geoffrey Gueret"
__contact__ = "geoffrey@mailq.io"
__copyright__ = "Copyright (C) 2013  Geoffrey Gueret"

__license__ = "GPL"
__version__ = "0.1.a"
__status__ = "Development"


# Consumer handle and reply tasks.
from .consumer import Consumer

# Producer initiate task, by calling the consumer.
from .producer import Producer

# Observer inspect replies maked by the consumer (asked by the producer).
from .observer import Observer
