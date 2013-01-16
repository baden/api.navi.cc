# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
#from db.account import Account
#from db.system import System
from db.logs import Logs
#import base64
#import json
#import logging


@Route(BaseHandler.API_PREFIX + r"/logs/(?P<skey>[^\/]*)")
class LogsGet(BaseHandler):
    @BaseHandler.auth
    def get(self, skey):
        # TODO! Добавить проверку на право просмотра

        limit = int(self.request.arguments.get("limit", "100"))

        logs, cursor = Logs(cached=False).get_for_skey(skey, limit=limit)

        self.writeasjson({
            "logs": logs,
            "cursor": {
                "dir": dir(cursor),
                "count": cursor.count(),
                "explain": cursor.explain(),
                "alive": cursor.alive,
                "id": cursor.cursor_id,
            }
        })
