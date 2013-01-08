#!/usr/bin/env python
# -*- coding: utf-8 -

import base64
import pickle
#from bson import Binary
from time import time
import json


class System(object):
    def __init__(self, db, redis):
        self.col = db.collection("system")
        # _id используется как ключ skey
        self.redis = redis

    @staticmethod
    def imei_to_key(imei):
        return base64.urlsafe_b64encode(str(imei))

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

    def get(self, skey):
        s = self.redis.get('system.%s' % skey)
        if s is not None:
            return pickle.loads(s)
        else:
            s = self.col.find_one({"_id": skey})
            if s is not None:
                self.redis.set('system.%s' % skey, pickle.dumps(s))
                return s
        return None

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
            self.redis.set('system.%s' % skey, pickle.dumps(s))
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
