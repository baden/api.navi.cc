#!/usr/bin/env python
# -*- coding: utf-8 -

import base64
import sha
import pickle
from time import time
import json
import logging

SHA_SALT = 'some_salt_for_secure'


class Account(object):
    def __init__(self, db, redis):
        self.col = db.collection("account")
        # _id используется как ключ akey
        #self.col.ensure_index([
        #    ("skey", 1),
        #])
        self.redis = redis

    @staticmethod
    def name_pass_to_akey2(domain, name, password):
        s = sha.sha()
        s.update(name)
        s.update(password)
        s.update(SHA_SALT)
        return s.hexdigest()
        return base64.urlsafe_b64encode(str(s.digest()))

    @staticmethod
    def name_pass_to_akey(domain, name, password):
        s = sha.sha()
        s.update(name)
        s.update(password)
        s.update(SHA_SALT)
        return base64.urlsafe_b64encode(domain + ":" + s.hexdigest())

    @staticmethod
    def get_domain(akey):
        #logging.info("get_domain(%s)", akey)
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

    def get(self, akey):
        s = self.redis.get('account.%s' % akey)
        #logging.info("===> account.%s = %s" % (akey, s))
        if s is not None:
            #logging.info("===> account.%s = %s" % (akey, s))
            return pickle.loads(s)
        else:
            s = self.col.find_one({"_id": akey})
            if s is not None:
                self.redis.set('account.%s' % akey, pickle.dumps(s))
                return s
        return None

    def add_system(self, akey, skey):
        self.redis.delete('account.%s' % akey)
        self.col.update({"_id": akey}, {"$push": {"skeys": skey}})

    def del_system(self, akey, skey):
        self.redis.delete('account.%s' % akey)
        self.col.update({"_id": akey}, {"$pull": {"skeys": skey}})

    def sort_systems(self, akey, skeys):
        self.redis.delete('account.%s' % akey)
        self.col.update({"_id": akey}, {"$set": {"skeys": skeys}})

    def create(self, domain, name, password):
        akey = Account.name_pass_to_akey(domain, name, password)
        a = self.get(akey)
        if a is not None:   # Пользоваетль с таким именем уже существует
            return a
        s = {
            "_id": akey,
            "domain": domain,
            "name": name,               # TODO! Не забыть это убрать!!!
            "password": password,       # TODO! Не забыть это убрать!!!
            "date": int(time()),        # Дата создания записи
            "title": name,              # Отображаемое имя пользователя
            "desc": {},                 # Произвольные записи информации о пользователе
            "premium": int(time()),     # Дата окончания премиум-подписки
            "config": {},               # Персональные параметры конфигурации, тема сайта, параметры отображения и т.п.
            "skeys": [],                # Список наблюдаемых систем (массив ключей)
            "admin": False,             # Права администрирования. Администратор может иметь право просматривать список пользователей домена, и возможно управлять ими.
        }
        self.col.insert(s)
        return s

    def get_to_json(self, akey):
        s = Account.filter(self.get(akey))
        if s is None:
            return json.dumps({})
        return json.dump(s, indent=2)

    def getall(self):
        return self.col.find()
        #aa = self.col.find()
        #return [a for a in aa if a.get("domain", "") == domain]
