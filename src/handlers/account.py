#!/usr/bin/env python
# -*- coding: utf-8 -

from route import Route
from base import BaseHandler
from db.account import Account
from db.system import System
import base64
import json
import logging


#@Route(r"/api/account/new/(?P<domain>[^\/]*)/(?P<user>[^\/]+)/(?P<password>[^\/]+)")
@Route(r"/api/account/new")
class AccountNew(BaseHandler):
    def apiget(self):
        #domain = self.get_argument("domain", "")
        user = self.get_argument("user", "u")
        password = self.get_argument("password", "")

        akey = Account.name_pass_to_akey(self.domain, user, password)
        account = self.application.account.get(akey)
        result = "created"
        if account is not None:
            result = "already"
        else:
            account = self.application.account.create(self.domain, user, password)
        account = Account.filter(account)
        account["systems"] = dict([(skey, System.filter(self.application.system.get(skey), domain=self.domain)) for skey in account["skeys"]])
        info = {
            "result": result,
            "user": user,
            "password": password,
            "akey": akey,  # self.application.account.get(),
            "account": account,
            #"akey2": Account.name_pass_to_akey2(user, password),  # self.application.account.get(),
            #"rakey": base64.urlsafe_b64decode(akey).encode('hex')
        }
        return info


@Route(r"/api/account/get")
class AccountGet(BaseHandler):
    def apiget(self):
        #akey = Account.name_pass_to_akey(user, password)
        akey = self.get_argument("akey", "")
        # TODO! Check for self.domain == domain
        #domain = Account.get_domain(akey)
        #domain = self.domain
        account = Account.filter(self.application.account.get(akey))
        #systems = {}
        #for skey in account["skeys"]:
        #    systems[skey] = System.filter(self.application.system.get(skey), domain=self.domain)
        #systems = dict([(skey, System.filter(self.application.system.get(skey), domain=domain)) for skey in account["skeys"]])
        account["systems"] = dict([(skey, System.filter(self.application.system.get(skey), domain=self.domain)) for skey in account["skeys"]])
        info = {
            "akey": akey,  # self.application.account.get(),
            "account": account,
            #"akey2": Account.name_pass_to_akey2(user, password),  # self.application.account.get(),
            #"rakey": base64.urlsafe_b64decode(akey).encode('hex')
        }
        return info


@Route(r"/api/account/getall/(?P<domain>.*)")
class AccountGet(BaseHandler):
    def apiget(self, domain):
        accounts = self.application.account.getall()
        info = {
            "accounts": [Account.filter(a) for a in accounts if a.get("domain", "") == domain],
            #"akey2": Account.name_pass_to_akey2(user, password),  # self.application.account.get(),
            #"rakey": base64.urlsafe_b64decode(akey).encode('hex')
        }
        return info


@Route(r"/api/account/systems/add")
class AccountNew(BaseHandler):
    def apiget(self):
        akey = self.get_argument("akey", "=")
        imei = self.get_argument("imei", "")

        #domain = Account.get_domain(akey)
        #TODO Check akey for domain

        account = Account.filter(self.application.account.get(akey))

        skey = System.imei_to_key(imei)

        if skey in account["skeys"]:
            return {
                "result": "already"
            }

        system = System.filter(self.application.system.get(skey), domain=self.domain)
        if system is None:
            return {
                "result": "notfound"
            }

        self.application.account.add_system(akey, skey)

        info = {
            "error": "not impliment",
            #"account": account,
            "system": system
        }
        return info


@Route(r"/api/account/systems/del")
class AccountNew(BaseHandler):
    def apiget(self):
        akey = self.get_argument("akey", "=")
        skey = self.get_argument("skey", "=")

        account = Account.filter(self.application.account.get(akey))
        if skey not in account["skeys"]:
            return {
                "result": "notfound"
            }
        self.application.account.del_system(akey, skey)

        info = {
            "result": "deleted"
            #"account": account
        }
        return info


@Route(r"/api/account/systems/sort")
class AccountNew(BaseHandler):
    def apipost(self):
        akey = self.get_argument("akey", "=")
        logging.info('==self.request.arguments:%s', repr(self.request.arguments))
        #skeys = json.loads(self.get_argument("skeys", "[]"))
        skeys = self.get_arguments("skeys", [])
        logging.info('==skeys:%s', repr(skeys))

        #account = Account.filter(self.application.account.get(akey))
        self.application.account.sort_systems(akey, skeys)
        info = {
            "result": "sorted",
            #"account": account,
            "skeys": skeys
        }
        return info
