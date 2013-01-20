# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.system import System
from tornado.web import HTTPError

import logging


@Route(BaseHandler.API_PREFIX + r"/system/(?P<skey>[^\/]+)")
class APISystem(BaseHandler):

    schema = {}
    schema["PATCH"] = {
        "title": "patch system",
        "type": "object",
        "properties": {
            "desc": {
                "type": "string",
                "required": True
            }
        },
        "additionalProperties": False
    }

    @BaseHandler.auth
    def patch(self, skey):
        System(skey).change_desc(self.payload["desc"], domain=self.domain)

        self.writeasjson({
            "skey": skey,
            "domain": self.domain,
        })
