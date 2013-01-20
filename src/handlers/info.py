#!/usr/bin/env python
# -*- coding: utf-8 -

from route import Route
from base import BaseHandler
from time import time
import pickle
from tornado.web import RequestHandler, asynchronous


api_version = "1.0"

from config import MONGO_URL, MONGO_DATABASE, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_SOCKET_PATH


from redis import Redis
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, unix_socket_path=REDIS_SOCKET_PATH)

import base64
import sha
import hashlib
import hmac


SHA_SECRET = 'some_data_for_secure'

'''
_UTF8_TYPES = (bytes, type(None))


def utf8(value):
    if isinstance(value, _UTF8_TYPES):
        return value
    assert isinstance(value, unicode)
    return value.encode("utf-8")


def _create_signature(secret, *parts):
    hash = hmac.new(utf8(secret), digestmod=hashlib.sha1)
    for part in parts:
        hash.update(utf8(part))
    return utf8(hash.hexdigest())


def create_signed_value(secret, name, value):
    timestamp = utf8(str(int(time.time())))
    value = base64.b64encode(utf8(value))
    signature = _create_signature(secret, name, value, timestamp)
    value = b("|").join([value, timestamp, signature])
    return value
'''


@Route(BaseHandler.API_PREFIX + r"/info")
class Info(BaseHandler):

    def get(self):
        #self.set_coockies()
        self.set_secure_cookie("counter", "0")

        s = sha.sha()
        #s.update(name)
        #s.update(password)
        #s.update(SHA_SALT)

        self.writeasjson({
            "api_version": api_version,
            "identity": self.identity,
            #"identity2": self.identity2,
            "self": {
                #"dir": dir(self),
            },
            "request": {
                #"dir": dir(self.request),
                "cookies": self.request.cookies,
                "headers": self.request.headers,
                "remote_ip": self.request.remote_ip
            },
            "user": {
                "cookie": self.get_secure_cookie("user", ""),
            },
            "auth": base64.urlsafe_b64encode(s.hexdigest()).rstrip('='),
            "akey": self.create_signed_value('user', 'abc'),
            "get": self.decode_signed_value('akey', 'YzI5dFpTMXphWFJsWDJOdmJUb3pOVGN6TnpNd01HTXlNVEEyTkRReU56TmxOVGc1TXpBd1pUTXhOMlppWVRkak1EUTVObUZp|1358105291|4ed8aeaccf463c504c999cced6000e123ae3907d'),
            "server_time": int(time())
        })


@Route(BaseHandler.API_PREFIX + r"/check")
class Check(BaseHandler):

    def get(self):
        #self.set_coockies()
        #self.set_secure_cookie("counter", "0")

        self.writeasjson({
            "api_version": api_version,
            "request": {
                #"dir": dir(self.request),
                "cookies": self.request.cookies,
                "headers": self.request.headers,
                "remote_ip": self.request.remote_ip
            },
            "user": {
                "cookie": self.get_secure_cookie("user", ""),
            },
            "server_time": int(time())
        })


@Route(BaseHandler.API_PREFIX + r"/admin/flushcache")
class FlushCache(BaseHandler):
    def get(self):
        redis.flushall()
        self.writeasjson({
            "result": "flushed"
        })


@Route(BaseHandler.API_PREFIX + r"/admin/redis")
class Redis(BaseHandler):
    def get(self):
        keys = redis.keys()
        values = {}
        for k in keys:
            v = redis.get(k)
            try:
                o = pickle.loads(v)
            except:
                o = v
            values[k] = o
        self.writeasjson({
            "keys": keys,
            "values": values,
            "info": redis.info(),
            "ping": redis.ping()
        })


@Route(BaseHandler.API_PREFIX + r"/admin/pickle")
class Pickle(BaseHandler):
    def get(self):
        value = redis.get(self.get_argument("key", "x"))
        if value is not None:
            data = pickle.loads(value)
        else:
            data = None
        self.writeasjson({
            "raw": value,
            "data": data
        })


@Route(BaseHandler.API_PREFIX + r"/testtimeout")
class TestTimeout(RequestHandler):
    @asynchronous
    def get(self):
        from tornado.ioloop import IOLoop
        from datetime import timedelta

        self.counter = 150

        def send():
            try:
                self.write(".")
            except:
                self.finish()
                return

            self.counter = self.counter - 1
            if self.counter > 0:
                IOLoop.instance().add_timeout(timedelta(0, 1), send)
            else:
                self.finish()

        send()

        #send()
