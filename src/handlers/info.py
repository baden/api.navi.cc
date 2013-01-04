#!/usr/bin/env python
# -*- coding: utf-8 -

from route import Route
from base import BaseHandler
from time import time
import pickle

api_version = "1.0"


@Route(r"/api/info")
class Info(BaseHandler):
    def apiget(self):

        msg = {
            "id": 0,
            "message": "get_info"
        }
        self.application.publisher.send(msg)

        return {
            "api_version": api_version,
            "server_time": int(time())
        }


@Route(r"/api/flushcache")
class Info(BaseHandler):
    def apiget(self):
        redis = self.application.account.redis.flushall()
        return {
            "result": "flushed"
        }


@Route(r"/api/pickle")
class Info(BaseHandler):
    def apiget(self):
        redis = self.application.account.redis
        value = redis.get(self.get_argument("key", "x"))
        if value is not None:
            data = pickle.loads(value)
        else:
            data = None
        return {
            #"redis": dir(redis),
            "raw": value,
            "data": data
        }
