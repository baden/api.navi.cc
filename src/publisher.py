#!/usr/bin/env python
# -*- coding: utf-8 -

from zmq.eventloop import ioloop
ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq
import logging

from config import PUBLISHER_SUB


class Publisher(object):
    def __init__(self):
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        #publisher.bind("ipc:///tmp/ws_sub")
        self.publisher.connect(PUBLISHER_SUB)
        self.publish_stream = ZMQStream(self.publisher)

    def send(self, msg):
        logging.debug('Publisher:send(%s)' % repr(msg))
        self.publish_stream.send_pyobj(msg)
