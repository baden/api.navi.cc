# -*- coding: utf-8 -*-
import logging
from pymongo import MongoClient, uri_parser
from libraries.database import BaseCollection, Redis
from libraries.logger import log_event

__author__ = 'maxaon'
import libraries.web as web
import libraries.database as database

from .controllers import *

class Application(web.Application):
    logger = logging.getLogger(__name__ + ".Application")

    @log_event(logger, message_before="Application bootstrap", message_after=None)
    def bootstrap(self):
        super(Application, self).bootstrap()
        if 'db' in self.settings:
            self.bootstrap_db(**self.settings['db'])
        if 'redis' in self.settings:
            self.bootstrap_redis(**self.settings['redis'])
        if 'zmq' in self.settings:
            self.bootstrap_zmq(**self.settings['zmq'])
        self.bootstrap_session(**self.settings.get('session', {}))
        return self

    def bootstrap_db(self, **params):
        db_name = params.get('name')
        del params['name']
        if not db_name:
            res = uri_parser.parse_uri(params['host'])
            db_name = res['database']
        self.db = database.Database(MongoClient(**params), db_name)
        BaseCollection._db = self.db

    def bootstrap_redis(self, **param):
        from libraries.database import Redis

        self.redis = Redis(**param)

    def bootstrap_zmq(self, **param):
        pass

    def bootstrap_session(self, **param):
        from libraries.session import SessionManager

        if not 'redis' in param:
            raise ValueError("Redis configuration for session not supplied")
        redisConf = param['redis']
        if not 'db' in redisConf:
            raise ValueError("DB must be selected for redis session config")
        SessionManager._redis = Redis(**redisConf)
        SessionManager._db_name = param.get("db_name", 'db_sessions')

    @log_event(logger)
    def run(self, **kwargs):
        super(Application, self).run(**kwargs)




