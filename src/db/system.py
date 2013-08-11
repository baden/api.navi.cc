#!/usr/bin/env python
# -*- coding: utf-8 -

import base64
import pickle
#from bson import Binary
from time import time
import json
import logging

from base import DBBase


class System(DBBase):

    @staticmethod
    def imei_to_key(imei):
        return base64.urlsafe_b64encode(str(imei)).rstrip('=')

    @classmethod
    def create_or_update(cls, imei, **kwargs):
        logging.info("System.create_or_update(%s, %s)", str(imei), repr(kwargs))
        skey = cls.imei_to_key(imei)
        system = cls.get(key=skey, cached=True)
        logging.info("  skey=%s  system=%s", str(skey), repr(system))

        #TODO! Добавить обновление из kwargs телефона и других "редко-изменяемых" параметров
        #TODO! Добавить обработку "часто-изменяемых" параметров

        if system.isNone:
            system.insert({
                "_id": skey,
                "imei": imei,               # IMEI. Не используется для идентификации, сохранено для удобства
                "phone": u"Не определен",   # Телефон карточки системы
                "date": int(time()),        # Дата создания записи (обычно первый выход на связь)
                "premium": int(time()),     # Дата окончания премиум-подписки
                # Ярлыки объекта (вместо групп)
                # Значения представляют собой записи вида:
                # {"домен": ["тэг1", "тэг2", ..., "тэгN"], "домен2': [...], ...}
                "tags": {},
                # Представляет собой словарь значений {"домен1": "описание1", "домен2": "описание2", ...}
                "descbydomain": {},
                # Пиктограмма {"домен1": "пиктограмма", "домен2": "пиктограмма", ...}
                "icon": {},
            })
        return system

    def filter(self, domain=None):
        if self.document is None:
            return None
        a = self.document.copy()

        a["skey"] = a["_id"]
        a["key"] = a["_id"]
        del a["_id"]
        if domain is not None:
            a["desc"] = a["descbydomain"].get(domain, u"Система %s" % a["imei"])
            del a["descbydomain"]
        self.dynamic(a)
        return a

    def find_all(self, keys, domain=None):
        systems = super(System, self).find_all(keys)
        for k, a in systems.iteritems():
            if a is not None:
                a["skey"] = a["_id"]
                a["key"] = a["_id"]
                del a["_id"]
                if domain is not None:
                    a["desc"] = a["descbydomain"].get(domain, u"Система %s" % a["imei"])
                    del a["descbydomain"]
                # logging.info('add dynamic data for %s' % str(a["key"]))
                self.dynamic(a)
        return systems

    def dynamic(self, system):
        prefix = self.__class__.__name__ + "_dynamic"
        key = system["key"]
        dynamic = self.redis.hgetall('%s.%s' % (prefix, key))
        system['dynamic'] = dynamic

    def change_desc(self, desc, domain=None):
        logging.info(' Change desc (%s, %s, %s)', self.key, desc, domain)
        self.reset_cache()
        self.collection.update(
            {
                "_id": self.key
            },
            {
                "$set": {
                    "descbydomain." + str(domain): desc
                }
            }, upsert=True
        )

    def change_params(self, params):
        logging.info(' Change params (%s, %s)', self.key, params)
        self.reset_cache()
        self.collection.update(
            {
                "_id": self.key
            },
            {
                "$set": {
                    "params": params
                }
            }, upsert=True
        )

    '''
    def __init__(self, db, redis):
        self.col = db.collection("system")
        # _id используется как ключ skey
        self.redis = redis
    '''

    '''

    @staticmethod
    def key_to_imei(skey):
        return base64.urlsafe_b64decode(str(skey))

    @staticmethod
    def filter(system, domain=None):
        if system is None:
            return None
        a = system.copy()
        a["skey"] = a["_id"]
        a["key"] = a["_id"]
        del a["_id"]
        if domain is not None:
            a["desc"] = a["descbydomain"].get(domain, u"Система %s" % system["imei"])
            del a["descbydomain"]
        #del a["name"]
        #del a["password"]
        return a

    @cached_by_redis
    def get(self, skey):
        return self.col.find_one({"_id": skey})

    def get_by_imei(self, imei):
        return self.get(System.imei_to_key(imei))

    def get_by_imei_or_create(self, imei):
        s = self.get_by_imei(imei)
        if s is None:
            skey = System.imei_to_key(imei)
            s = {
                "_id": skey,
                "imei": imei,               # IMEI. Не используется для идентификации, сохранено для удобства
                "phone": u"Не определен",   # Телефон карточки системы
                "date": int(time()),        # Дата создания записи (обычно первый выход на связь)
                "premium": int(time()),     # Дата окончания премиум-подписки
                # Ярлыки объекта (вместо групп)
                # Значения представляют собой записи вида:
                # {"домен": ["тэг1", "тэг2", ..., "тэгN"], "домен2': [...], ...}
                "tags": {},
                # Представляет собой словарь значений {"домен1": "описание1", "домен2": "описание2", ...}
                "descbydomain": {},
                # Пиктограмма {"домен1": "пиктограмма", "домен2": "пиктограмма", ...}
                "icon": {},
            }
            self.col.save(s)
            #self.redis.set('system.%s' % skey, pickle.dumps(s))
        return s

    def skey_by_imei_or_create(self, imei):
        return self.get_by_imei_or_create(imei)["_id"]

    def get_to_json(self, skey):
        s = self.get(skey)
        if s is None:
            return json.dumps({})
        s["skey"] = s["_id"]
        del s["_id"]
        return json.dump(s, indent=2)

    def get_all_to_json(self):
        ss = [s for s in self.col.find()]
        for s in ss:
            s["skey"] = s["_id"]
            del s["_id"]
        return json.dump(ss, indent=2)

    @reset_cache
    def change_desc(self, skey, desc, domain=None):
        self.col.update({"_id": skey}, {"$set": {"descbydomain." + str(domain): desc}}, upsert=True)
    '''
