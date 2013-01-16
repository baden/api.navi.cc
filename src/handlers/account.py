#!/usr/bin/env python
# -*- coding: utf-8 -

from route import Route
from base import BaseHandler
from db.account import Account
from db.system import System
#import base64
#import json
import logging


#@Route(r"/api/account/new")
@Route(BaseHandler.API_PREFIX + r"/login")
class AccountLogin(BaseHandler):
    def post(self):
        #username = self.request.arguments.get("username")
        #password = self.request.arguments.get("password")
        username = self.get_argument("username")
        password = self.get_argument("password")

        # Ключ должен сожержать sefl.identyty
        #identity = self.create_signed_value('user', 'abc')
        account = Account.by_name_pass(self.domain, username, password)
        #logging.info("account=%s", account)
        result = "created"
        if account.isNone:
            account.create(self.domain, username, password)
        else:
            result = "already"

        access_token = self.create_signed_value('access_token', account.key + '@' + str(self.identity))
        self.set_secure_cookie("counter", "0")
        self.set_cookie('access_token', access_token)

        self.writeasjson({
            "result": result,
            #"akey": account.key,
            "access_token": access_token,
            "account": account.filter(),
        })


@Route(BaseHandler.API_PREFIX + r"/logout")
class AccountLogout(BaseHandler):
    def post(self):
        self.set_cookie('access_token', '')
        #self.clear_cookie('access_token', '')
        self.writeasjson({
            "result": 'logout',
        })


# TODO! Написать wraper для указания необходимости авторизации


@Route(BaseHandler.API_PREFIX + r"/account")
class AccountGet(BaseHandler):
    @BaseHandler.auth
    def get(self):
        self.writeasjson({
            "account": self.account.filter(),
        })


@Route(BaseHandler.API_PREFIX + r"/account/getall/(?P<domain>.*)")
class AccountGetAll(BaseHandler):
    def get(self, domain):
        accounts = Account.getall()
        self.writeasjson({
            "accounts": [Account.static_filter(a) for a in accounts if a.get("domain", "") == domain],
        })


@Route(BaseHandler.API_PREFIX + r"/account/systems")
class AccountSystem(BaseHandler):
    @BaseHandler.auth
    def post(self):
        cmd = self.request.arguments.get("cmd", '')
        logging.info("AccountSystem.post[{cmd:%s}]", cmd)

        if cmd == '':

            self.writeasjson({
                "error": "cmd paramenter is required"
            })

        elif cmd == 'add':

            imeis = self.request.arguments.get("imeis")
            logging.info(' == imeis=%s', repr(imeis))

            results = []

            skeys = [System.imei_to_key(imei) for imei in imeis]
            systems = System(key=None, cached=True).find_all(skeys, domain=self.domain)
            pushAll = []

            for skey, system in systems.iteritems():
                if skey in self.account.document["skeys"]:
                    results.append({
                        "result": "already"
                        })
                else:
                    if system is None:
                        results.append({
                            "result": "notfound"
                            })
                    else:
                        pushAll.append(skey)
                        results.append({
                            "result": "added",
                            "system": system
                        })
            self.account.add_systems(pushAll)

            '''
            for imei in imeis:
                skey = System.imei_to_key(imei)

                if skey in self.account.document["skeys"]:
                    results.append({
                        "result": "already"
                        })
                else:
                    system = System.get(skey).filter(domain=self.domain)
                    if system is None:
                        results.append({
                            "result": "notfound"
                            })
                    else:
                        self.account.add_system(skey)

                        results.append({
                            "result": "added",
                            "system": system
                        })
            '''

            self.writeasjson({
                "systems": results
            })

        elif cmd == 'sort':

            skeys = self.request.arguments.get("skeys", [])

            self.account.sort_systems(skeys)
            self.writeasjson({
                "result": "sorted",
                "skeys": skeys
            })

        else:

            self.writeasjson({
                "error": "cmd must be set"
            })


@Route(BaseHandler.API_PREFIX + r"/account/systems/(?P<skey>[^\/]+)")
class AccountSystemKey(BaseHandler):
    @BaseHandler.auth
    def delete(self, skey):
        self.account.del_system(skey)
        self.writeasjson({
            "result": "deleted"
        })
