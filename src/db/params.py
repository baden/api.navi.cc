# -*- coding: utf-8 -*-
import logging

#import config
#from config import MONGO_URL
from base import DBBase
import json


class Params(DBBase):
    col = 'params'

    def __init__(self, skey):
        logging.info('Params.__init__(%s)', skey)
        super(Params, self).__init__(skey)

    def from_json(self):
        try:
            r = json.loads(self.document["save"])
        except:
            r = None
        return r

    def all(self):
        del self.document["_id"]
        del self.document["__cache__"]
        result = {}
        for (k,v) in self.document.iteritems():
            result[DBBase.fromkey(k)] = v
        return result

    def add_queue(self, key, value):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$set": {DBBase.tokey(key) + ".queue": value}}, True)

    def del_queue(self, key):
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$unset": {DBBase.tokey(key) + ".queue": ""}})

    @classmethod
    def del_queueall(cls, skey):
        self = cls.get(skey)
        result = {}
        for (k, v) in self.document.iteritems():
            if k not in ["_id", "__cache__"]:
                if v.has_key("queue"):
                    result[k + ".queue"] = ""
        # logging.info("unset =%s" % repr(result))
        self.reset_cache()
        self.collection.update({"_id": self.key}, {"$unset": result})
