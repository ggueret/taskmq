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


class SerializerRegistry(object):

    def __init__(self):
        self.encoders = {}
        self.decoders = {}

    def register(self, name, encoder, decoder, content_type, content_encoding):
        self.encoders[name] = (content_type, content_encoding, encoder)
        self.decoders[content_type] = decoder

    def decode(self, content_type, content_encoding, content):
        return self.decoders[content_type](content)

    def encode(self, content, serializer=None):
        serializer = serializer or self.encoders.keys()[0]
        content_type, content_encoding, encoder = self.encoders[serializer]
        return (content_type, content_encoding, encoder(content))


serialize = SerializerRegistry()


def register_json():
    """Register JSON serializer"""
    try:
        from ujson import dumps, loads
    except ImportError:
        from json import dumps, loads
    serialize.register(
        name='json',
        encoder=dumps,
        decoder=loads,
        content_type='application/json',
        content_encoding='utf-8'
    )

register_json()
