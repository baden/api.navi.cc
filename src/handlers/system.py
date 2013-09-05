# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.system import System
from tornado.web import HTTPError

import logging


@Route(BaseHandler.API_PREFIX + r"/system/(?P<skey>[^\/]+)")
class APISystem(BaseHandler):

    schema = {}

    @BaseHandler.auth
    def get(self, skey):
        value = System.get(skey).filter(domain=self.domain) #.all()
        self.writeasjson({
            "skey": skey,
            "value": value,
        })


    schema["PATCH"] = {
        "title": "patch system",
        "type": "object",
        "properties": {
            "desc": {
                "type": "string",
                "required": False
            },
            "icon": {
                "type": "string",
                "required": False
            },
            "params": {
                "type": "object",
                "required": False
            }
        },
        "additionalProperties": False
    }

    @BaseHandler.auth
    def patch(self, skey):

        if "desc" in self.payload:
            System(skey).change_desc(self.payload["desc"], domain=self.domain)

            self.writeasjson({
                "skey": skey,
                "domain": self.domain,
            })
        elif "icon" in self.payload:
            icon = self.payload["icon"]
            System(skey).patch("icon", icon)
            self.writeasjson({
                "skey": skey,
                "icon": icon,
            })
        elif "params" in self.payload:
            params = self.payload["params"]
            logging.info("System params=%s" % repr(params))
            System(skey).change_params(params)

            self.writeasjson({
                "skey": skey
            })
