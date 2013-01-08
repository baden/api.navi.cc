# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.account import Account
from db.system import System
import base64
import json
import logging


@Route(r"/api/system/changedesc")
class SystemChangeDesc(BaseHandler):
    def apiget(self):
        skey = self.get_argument("skey", "=")
        '''
        # TODO! Добавить проверку на право просмотра
        akey = self.get_argument("akey", "")
        domain = Account.get_domain(akey)
        #account = Account.filter(self.application.account.get(akey))

        self.application.system.get(skey)
        '''

        domain = self.request.host.split(':')[0]

        info = {
            "result": "not_implemented_yet",
            "skey": skey,
            "domain": domain,
            "request": {
                "dir": dir(self.request),
                "connection": {
                    "dir": dir(self.request.connection),
                    "address": self.request.connection.address,
                    "xheaders": self.request.connection.xheaders
                },
                "headers": repr(self.request.headers),
                "uri": str(self.request.uri),
                "full_url": str(self.request.full_url),
                "path": str(self.request.path),
                "host": str(self.request.host)
            }
        }
        return info

