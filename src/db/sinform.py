# -*- coding: utf-8 -*-
"""
    Сообщения для систем. Наподобие:
    CONFIGUP - для обновления конфигурации.
    FWUPDATE - для обновления прошивки

"""

from base import redis

REDIS_PREFIX = "SINFORM"

def sinform_set(skey, message):
    redis.sadd('%s.%s' % (REDIS_PREFIX, skey), message)

def sinform_unset(skey, message):
    redis.srem('%s.%s' % (REDIS_PREFIX, skey), message)

def sinform_getall(skey):
    return redis.smembers('%s.%s' % (REDIS_PREFIX, skey))
