# -*- coding: utf-8 -*-

#import db
#print "db:logs:import", repr(db)

import logging
from base import DBBase


class Logs(DBBase):
    def __init__(self, *args, **kwargs):
        super(Logs, self).__init__(*args, **kwargs)
        self.collection.ensure_index([
            ("skey", 1), ("dt", 1)
        ])

    def add(self, log):
        self.collection.insert(log)

    def get_for_skey(self, skey, limit=100):
        logging.info('Logs.query(%s)', skey)
        query = self.collection.find({'skey': skey}).sort('dt', -1).limit(limit)
        logging.info("query=%s", dir(query))
        logs = []
        for l in query:
            l["lkey"] = str(l["_id"])
            del l["_id"]
            logs.append(l)
        return logs, query
