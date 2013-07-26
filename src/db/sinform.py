# -*- coding: utf-8 -*-
"""
    Сообщения для систем. Наподобие:
    CONFIGUP - для обновления конфигурации.
    FWUPDATE - для обновления прошивки

"""

from base import redispool
import redis
# from redis import Redis

r = redis.Redis(connection_pool = redispool)

REDIS_PREFIX = "SINFORM"

def sinform_set(skey, message):
    r.sadd('%s.%s' % (REDIS_PREFIX, skey), message)

def sinform_unset(skey, message):
    r.srem('%s.%s' % (REDIS_PREFIX, skey), message)

def sinform_getall(skey):
    return r.smembers('%s.%s' % (REDIS_PREFIX, skey))
