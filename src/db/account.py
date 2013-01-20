#!/usr/bin/env python
# -*- coding: utf-8 -

import base64
import sha
#import pickle
from time import time
import json
import logging

from base import DBBase

from system import System


#from cached import cached_by_redis, reset_cache

SHA_SALT = 'some_salt_for_secure'


def _f(value):
    return value.replace('|', '+')


class Account(DBBase):

    @classmethod
    def by_name_pass(cls, domain, name, password):
        akey = Account.name_pass_to_akey(domain, name, password)
        return cls.get(akey)

    @staticmethod
    def name_pass_to_akey(domain, name, password):
        s = sha.sha()
        s.update(domain)
        s.update(name)
        s.update(password)
        s.update(SHA_SALT)
        #return base64.urlsafe_b64encode(domain + ":" + s.hexdigest()).rstrip('=')
        return base64.urlsafe_b64encode(s.digest()).rstrip('=')

    def add_system(self, skey):
        if self.key is None:
            Exception("key must be set")
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$push": {"skeys": skey}})

    def add_systems(self, skeys):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$pushAll": {"skeys": skeys}})

    def del_system(self, skey):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$pull": {"skeys": skey}})

    def sort_systems(self, skeys):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$set": {"skeys": skeys}})

    def set_token(self, access_token):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$push": {"access_tokens": access_token}})

    def reset_token(self, access_token):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$pull": {"access_tokens": access_token}})

    def create(self, domain, name, password):
        if self.document is not None:   # Подавим пересоздание
            return
        akey = Account.name_pass_to_akey(domain, name, password)
        self.document = {
            "_id": akey,
            "domain": domain,
            "created_at": int(time()),  # Дата создания записи
            "title": name,              # Отображаемое имя пользователя
            "desc": {},                 # Произвольные записи информации о пользователе
            "premium": int(time()),     # Дата окончания премиум-подписки
            "config": {},               # Персональные параметры конфигурации, тема сайта, параметры отображения и т.п.
            "skeys": [],                # Список наблюдаемых систем (массив ключей)
            "role": "user",             # Права администрирования. Администратор может иметь право просматривать список пользователей домена, и возможно управлять ими.
            "access_tokens": []         # Авторизованные клиенты
        }
        self.collection.insert(self.document)

    def filter(self):
        if self.document is None:
            return None
        a = self.document.copy()
        a["akey"] = a["_id"]
        del a["_id"]
        if "password" in a:
            del a["password"]
        #a["systems"] = System(key=None, cached=True)
        a["systems"] = System(key=None, cached=True).find_all(a["skeys"], domain=a["domain"])
        #a["systems"] = dict([(skey, System.filter(System(skey), domain=a["domain"])) for skey in a["skeys"]])
        return a

    @staticmethod
    def static_filter(document):
        if document is None:
            return None
        a = document.copy()
        a["akey"] = a["_id"]
        del a["_id"]
        del a["password"]
        a["systems"] = System(key=None, cached=True).find_all(a["skeys"], domain=a["domain"])
        #a["systems"] = dict([(skey, System.filter(System(skey), domain=a["domain"])) for skey in a["skeys"]])
        return a

    def get_to_json(self, akey):
        s = Account.filter(self.get(akey))
        if s is None:
            return json.dumps({})
        return json.dump(s, indent=2)

    @classmethod
    def getall(cls):
        c = cls(key=None)
        return c.collection.find()
        #return None
        #aa = self.col.find()
        #return [a for a in aa if a.get("domain", "") == domain]

    """
    @staticmethod
    def get_domain(akey):
        #logging.info("get_domain(%s)", akey)
        modulo = len(akey) % 4
        if modulo != 0:
            akey += ('=' * (4 - modulo))
        s = base64.urlsafe_b64decode(str(akey))
        #logging.info("->get_domain(%s)", s)
        return s.split(':')[0]

    @staticmethod
    def filter(account):
        if account is None:
            return None
        a = account.copy()
        a["akey"] = a["_id"]
        del a["_id"]
        #del a["name"]
        del a["password"]
        return a

    @cached_by_redis
    def get(self, akey):
        return self.col.find_one({"_id": akey})

    @reset_cache
    def add_system(self, akey, skey):
        self.col.update({"_id": akey}, {"$push": {"skeys": skey}})

    @reset_cache
    def del_system(self, akey, skey):
        self.col.update({"_id": akey}, {"$pull": {"skeys": skey}})

    @reset_cache
    def sort_systems(self, akey, skeys):
        self.col.update({"_id": akey}, {"$set": {"skeys": skeys}})

    """
