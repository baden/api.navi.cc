# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
#from db.account import Account
#from db.system import System
#import base64
#import json
#import logging

from db.params import Params


@Route(BaseHandler.API_PREFIX + r"/params/(?P<skey>[^\/]*)")
class ParamsGet(BaseHandler):
    @BaseHandler.auth
    def get(self, skey):
        #value = Params.get(skey)
        #document = Params.get(skey).document
        value = Params.get(skey).from_json()
        self.writeasjson({
            "skey": skey,
            "value": value,
        })
