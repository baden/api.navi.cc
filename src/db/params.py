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
        logging.info("Update: %s, %s, %s" % (self.key, key, value))
        # self.collection.update({"_id": self.key}, {"$push": {"queue": {"key": key, "value": value}}}, True)
        #self.collection.update({"_id": self.key}, {"$set": {"queue." + DBBase.tokey(key): value}}, True)
        self.collection.update({"_id": self.key}, {"$set": {DBBase.tokey(key) + ".queue": value}}, True)

    def del_queue(self, key):
        self.collection.update({"_id": self.key}, {"$unset": {DBBase.tokey(key) + ".queue": ""}})

    # @classmethod
    # def save(cls, skey, object):
    #     #logging.info('Params.save(%s, %s)', str(imei), str(object))
    #     #logging.info('=== config=%s', str(MONGO_URL))
    #     #logging.info('=== db=%s', cls.db)

    #     super(Params, cls).save({'save': json.dumps(object)}, key=skey)

    """
    @classmethod
    def get(cls, skey):
        logging.info('=== find(%s)', str(skey))
        value = cls.find_by_key(skey)
        logging.info('=== value=%s', str(value))
        if value is None:
            return None
        return json.loads(value["save"])
    """
