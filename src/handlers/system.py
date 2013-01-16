# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.system import System

import logging


#@Route(r"/api/account/systems/del/(?P<akey>[^\/]+)/(?P<skey>[^\/]+)")
@Route(BaseHandler.API_PREFIX + r"/system/(?P<skey>[^\/]+)")
class APISystem(BaseHandler):
    @BaseHandler.auth
    def patch(self, skey):

        #skey = self.get_argument("skey", "=")
        desc = self.request.arguments.get("desc", None)

        logging.info('System PATH of %s (%s)', skey, repr(self.request.arguments))

        if desc is not None:
            System(skey).change_desc(desc, domain=self.domain)

        self.writeasjson({
            "result": "not_implemented_yet",
            "skey": skey,
            "domain": self.domain,
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
        })
