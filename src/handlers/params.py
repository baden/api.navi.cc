# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db import sinform
#from db.account import Account
#from db.system import System
#import base64
#import json
import logging

from db.params import Params


@Route(BaseHandler.API_PREFIX + r"/params/(?P<skey>[^\/]*)")
class ParamsGet(BaseHandler):
    @BaseHandler.auth
    def get(self, skey):
        value = Params.get(skey).all()
        self.writeasjson({
            "skey": skey,
            "value": value,
        })

@Route(BaseHandler.API_PREFIX + r"/params/queue/(?P<skey>[^\/]*)")
class ParamsGet(BaseHandler):
    schema = {}
    schema["POST"] = {
        "title": "post params/key",
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "required": True
            },
            "value": {
                "type": "string",
                "required": True
            }
        },
        "additionalProperties": True
    }

    """
        Отправляет значение в очередь параметров
    """
    @BaseHandler.auth
    def post(self, skey):
        key = self.request.arguments.get("key", '')
        value = self.request.arguments.get("value", '')
        Params(skey).add_queue(key, value)
        sinform.sinform_set(skey, "CONFIGUP")

        msg = {
            "message": "cfg_upd",
            "skey": skey
        }
        self.application.publisher.send(msg)

    """
        Очистить очередь
    """
    @BaseHandler.auth
    def delete(self, skey):
        Params.del_queueall(skey)
        sinform.sinform_unset(skey, "CONFIGUP")

        msg = {
            "message": "cfg_upd",
            "skey": skey
        }
        self.application.publisher.send(msg)


@Route(BaseHandler.API_PREFIX + r"/params/queue/(?P<skey>[^\/]*)/(?P<key>[^\/]*)")
class ParamsGet(BaseHandler):
    """
        Удалить одно значение из очереди
    """
    @BaseHandler.auth
    def delete(self, skey, key):
        Params(skey).del_queue(key)

        msg = {
            "message": "cfg_upd",
            "skey": skey
        }
        self.application.publisher.send(msg)
