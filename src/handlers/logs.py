# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
#from db.account import Account
#from db.system import System
from db.logs import Logs
#import base64
#import json
#import logging


@Route(BaseHandler.API_PREFIX + r"/logs/get/(?P<skey>.*)")
class LogsGet(BaseHandler):
    def get(self, skey):
        #skey = self.get_argument("skey", "=")
        # TODO! Добавить проверку на право просмотра
        #akey = self.get_argument("akey", "")
        #domain = Account.get_domain(akey)
        #account = Account.filter(self.application.account.get(akey))

        logs, cursor = Logs().get_for_skey(skey, limit=100)

        self.writeasjson({
            "result": "not_implemented_yet",
            "logs": logs,
            "cursor": {
                "dir": dir(cursor),
                "count": cursor.count(),
                "explain": cursor.explain(),
                "alive": cursor.alive,
                "id": cursor.cursor_id,
            }
        })
