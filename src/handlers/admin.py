# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.system import System
from tornado.web import HTTPError

import logging


@Route(BaseHandler.API_PREFIX + r"/admin/users")
class AdminUsers(BaseHandler):

    schema = {}

    # @BaseHandler.auth
    def get(self):
        # value = System.get(skey).filter(domain=self.domain) #.all()
        value = []
        self.writeasjson({
            "value": value,
        })
