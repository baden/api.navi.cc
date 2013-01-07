# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.account import Account
from db.system import System
import base64
import json
import logging


@Route(r"/api/system/logs/get")
class SystemGetLogs(BaseHandler):
    def apiget(self):
        skey = self.get_argument("skey", "=")
        # TODO! Добавить проверку на право просмотра
        akey = self.get_argument("akey", "")
        domain = Account.get_domain(akey)
        #account = Account.filter(self.application.account.get(akey))

        self.application.system.get(skey)

        info = {
            "result": "not_implemented_yet"
        }
        return info

