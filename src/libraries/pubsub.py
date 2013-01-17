# -*- coding: utf-8 -*-

from libraries.logger import log_event

from zmq.eventloop import ioloop

ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq

__author__ = 'maxaon'

class Publisher(object):
    @log_event(message_before="Publisher init. (disabled)", message_after=None)
    def __init__(self, config):
    #disabled
    #        self.context = zmq.Context(p)
    #        self.publisher = self.context.socket(zmq.PUB)
    #        #publisher.bind("ipc:///tmp/ws_sub")
    #        self.publisher.connect(PUBLISHER_SUB)
    #        self.publish_stream = ZMQStream(self.publisher)
        pass

    @log_event(message_before='Publisher(disabled):send({msg})', message_after=None, message_arguments=True)
    def send(self, msg):
        #self.publish_stream.send_pyobj(msg)
        pass


