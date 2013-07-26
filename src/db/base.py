#!/usr/bin/env python
# -*- coding: utf-8 -

import logging
from config import MONGO_URL, MONGO_DATABASE, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_SOCKET_PATH, DISABLE_CACHING
#from pymongo import Connection     # deprecated
from pymongo import MongoClient
import pickle
import redis

import time
import sys
if sys.platform == "win32":
    profiler_timer = time.clock     # On Windows, the best timer is time.clock()
else:
    profiler_timer = time.time      # On most other platforms the best timer is time.time()


class DBBase(object):

    connection = MongoClient(MONGO_URL)     # Single connection for all instanses
    # Use ConnectionPool for Redis connection
    if REDIS_HOST is not None:
        redispool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    db_start = profiler_timer()
    '''
    db = db
    redis = redis
    '''

    #connection = Connection(MONGO_URL)
    """
    db = connection[MONGO_DATABASE]
    if REDIS_HOST is not None:
        redis = redis.Redis(connection_pool=redispool)
    else:
        redis = redis.Redis(db=REDIS_DB, unix_socket_path=REDIS_SOCKET_PATH)
    db_stop = profiler_timer()
    """

    def __init__(self, key=None, cached=False):
        db_start = profiler_timer()
        #connection = MongoClient(MONGO_URL)
        self.db = self.connection[MONGO_DATABASE]
        if REDIS_HOST is not None:
            self.redis = redis.Redis(connection_pool=self.redispool)
        else:
            self.redis = redis.Redis(unix_socket_path=REDIS_SOCKET_PATH, db=REDIS_DB)
        db_stop = profiler_timer()
        logging.error("  db.delay=%f", db_stop - db_start)

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
        op_start = profiler_timer()
        rep.document = rep.find(key)
        op_stop = profiler_timer()
        logging.error("  op.delay=%f", op_stop - op_start)
        return rep

    def find(self, key):
        logging.info("db.base.find(%s, %s)" % (self.name, key))
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
            # logging.info("  mget result len=%d", len(cache))
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
            logging.info(' self name = %s' % self.name)
            logging.info(' coll name = %s' % self.collection.name)
            logging.info('== keys = %s' % repr(keys))
            # syss = self.collection.find({"_id": {"$in": keys}}).count()
            syss = self.collection.find({"_id": {"$in": ["dGVzdC0wMQ"]}}).count()
            logging.info('== syss = %s' % repr(syss))
            for s in self.collection.find({"_id": {"$in": keys}}):
                logging.info('== s = %s' % repr(s))
                s["__cache__"] = 'disabled'
                out[s["_id"]] = s

        for key in keys:
            if key not in out:
                out[key] = None
        return out

    def reset_cache(self):
        prefix = self.__class__.__name__
        logging.info('== RESET CACHE = %s.%s' % (repr(prefix), repr(self.key)))
        self.redis.delete('%s.%s' % (prefix, self.key))

    def update(self, param):
        self.reset_cache()
        self.collection.update({"_id": self.key}, param)

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

    @staticmethod
    def tokey(key):
        return key.replace(".", "#")

    @staticmethod
    def fromkey(key):
        return key.replace("#", ".")
