#!/usr/bin/env python
# -*- coding: utf-8 -

from route import Route
from base import BaseHandler
from db.account import Account
from db.system import System
#import base64
#import json
import logging


@Route(BaseHandler.API_PREFIX + r"/account")
class AccountGet(BaseHandler):
    schema = {}

    @BaseHandler.auth
    def get(self):
        self.writeasjson({
            "account": self.account.filter(),
        })

    schema["PATCH"] = {
        "title": "patch account",
        "type": "object",
        "properties": {
            "$set": {
                "type": "object",
                "required": False,
                "properties": {
                    "name": {
                        "type": "string",
                        "required": False
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    @BaseHandler.auth
    def patch(self):
        self.account.update(self.payload)
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
    schema = {}
    schema["POST"] = {
        "title": "post account/systems",
        "type": "object",
        "properties": {
            "cmd": {
                "type": "string",
                "required": True
            }
        },
        "additionalProperties": True
    }

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
            # logging.info(' == imeis=%s', repr(imeis))

            results = []

            skeys = [System.imei_to_key(imei) for imei in imeis]
            # logging.info(' == keys=%s', repr(skeys))
            systems = System(key=None, cached=True).find_all(skeys, domain=self.domain)
            # logging.info(' == systems=%s', repr(systems))
            pushAll = []

            for imei in imeis:
                skey = System.imei_to_key(imei)
                if skey in self.account.document["skeys"]:
                    results.append({
                        "result": "already"
                    })
                else:
                    #system = System.get(skey).filter(domain=self.domain)
                    if systems[skey] is None:
                        results.append({
                            "result": "notfound"
                        })
                    else:
                        pushAll.append(skey)
                        results.append({
                            "result": "added",
                            "system": systems[skey]
                        })
            self.account.add_systems(pushAll)

            self.writeasjson({
                "systems": results
            })

        elif cmd == 'sort':

            skeys = self.request.arguments.get("skeys", [])
            # logging.info("skeys = %s" % repr(skeys))
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
