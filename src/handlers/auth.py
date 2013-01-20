#!/usr/bin/env python
# -*- coding: utf-8 -

import logging

from route import Route
from base import BaseHandler
from db.account import Account


@Route(BaseHandler.API_PREFIX + r"/login")
class AccountLogin(BaseHandler):
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        account = Account.by_name_pass(self.domain, username, password)
        #logging.info("account=%s", account)
        result = "created"
        if account.isNone:
            account.create(self.domain, username, password)
        else:
            result = "already"

        access_token = self.create_signed_value(
            'access_token',
            account.key + '@' + str(self.identity)
        )
        #self.set_secure_cookie("counter", "0")
        self.set_cookie('access_token', access_token)
        account.set_token(access_token)

        self.writeasjson({
            "result": result,
            "access_token": access_token,
            "account": account.filter(),
        })


@Route(BaseHandler.API_PREFIX + r"/logout")
class AccountLogout(BaseHandler):
    @BaseHandler.auth
    def post(self):
        self.set_cookie('access_token', '')
        self.account.reset_token(self.access_token)
        #logging.error("Logout")
        # self.clear_cookie('access_token', '')
        self.writeasjson({
            "result": 'logout',
        })
