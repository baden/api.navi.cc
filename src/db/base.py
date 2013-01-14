#!/usr/bin/env python
# -*- coding: utf-8 -

import logging
from config import MONGO_URL, MONGO_DATABASE, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_SOCKET_PATH, DISABLE_CACHING
from pymongo import Connection
import pickle
from redis import Redis

connection = Connection(MONGO_URL)
db = connection[MONGO_DATABASE]
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, unix_socket_path=REDIS_SOCKET_PATH)


class DBBase(object):
    db = db
    redis = redis

    def __init__(self, key=None, cached=False):
        if DISABLE_CACHING:
            self.cached = False
        else:
            self.cached = cached
        self.name = self.__class__.__name__
        self.collection = self.db[self.name]
        #self.document = self.get_by_key(key)
        self.document = None
        if key is not None:
            self.document = {"_id": key}
        #logging.info("  + self.document=%s", repr(self.document))
        #logging.info("DBBase.__init__(%s, %s) as %s", str(key), str(cached), str(self.name))

    def __repr__(self):
        return "DB:'{0}' collection:'{0}' document:'{1}'".format(self.__class__.__name__, repr(self.document))

    @classmethod
    def get(cls, key, **kwargs):
        rep = cls(key, **kwargs)
        rep.document = rep.find(key)
        return rep

    def find(self, key):
        if key is None:
            return None

        if self.cached:
            prefix = self.__class__.__name__
            s = self.redis.get('%s.%s' % (prefix, key))
            if s is not None:
                try:
                    s = pickle.loads(s)
                    s["__cache__"] = 'from cache'
                except:
                    self.redis.delete('%s.%s' % (prefix, key))
                    s = None
                    logging.error('== error in pickle')
                return s
            else:
                s = self.collection.find_one({"_id": key})
                if s is not None:
                    self.redis.set('%s.%s' % (prefix, key), pickle.dumps(s))
                    s["__cache__"] = 'from db'
                    return s
            return None
        else:
            s = self.collection.find_one({"_id": key})
            if s is not None:
                s["__cache__"] = 'disabled'
            return s

    def find_all(self, keys):
        '''
            Возвращает словарь значений, где ключ-это значение из keys
        '''
        if keys is None:
            return {}
        if not isinstance(keys, list):
            return {}
        if len(keys) == 0:
            return {}

        #out = dict([(key, None) for key in keys])
        #return out

        out = {}
        if self.cached:
            prefix = self.__class__.__name__

            # Сначала пробуем получить все значения из кеша
            cache = self.redis.mget(('%s.%s' % (prefix, key) for key in keys))
            #logging.info("  mget result len=%d", len(cache))
            misskeys = []
            for i in range(len(keys)):
                s = cache[i]
                key = keys[i]
                if s is not None:
                    try:
                        s = pickle.loads(s)
                        s["__cache__"] = 'from cache'
                        out[key] = s
                    except:
                        self.redis.delete('%s.%s' % (prefix, key))
                        misskeys.append(key)
                        logging.error('== error in pickle')
                else:
                    misskeys.append(key)

            # Все значения, которые содержат None попытаемся загрузить из базы
            #logging.warning('== miss hits [%s]' % misskeys)
            if len(misskeys) != 0:
                for s in self.collection.find({"_id": {"$in": misskeys}}):
                    key = s["_id"]
                    self.redis.set('%s.%s' % (prefix, key), pickle.dumps(s))
                    s["__cache__"] = 'from db'
                    out[key] = s

        else:
            out = {}
            for s in self.collection.find({"_id": {"$in": keys}}):
                s["__cache__"] = 'disabled'
                out[s["_id"]] = s

        for key in keys:
            if key not in out:
                out[key] = None
        return out

    def reset_cache(self):
        prefix = self.__class__.__name__
        self.redis.delete('%s.%s' % (prefix, self.key))

    @property
    def isNone(self):
        return self.document is None

    @property
    def key(self):
        if self.document is None:
            return None
        return self.document["_id"]

    def insert(self, document):
        self.document = document
        self.collection.save(self.document)
