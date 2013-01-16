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

    @classmethod
    def save(cls, skey, object):
        #logging.info('Params.save(%s, %s)', str(imei), str(object))
        #logging.info('=== config=%s', str(MONGO_URL))
        #logging.info('=== db=%s', cls.db)

        super(Params, cls).save({'save': json.dumps(object)}, key=skey)

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
