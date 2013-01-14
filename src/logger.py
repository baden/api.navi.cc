#!/usr/bin/env python
# -*- coding: utf-8 -



from config import *

from mongolog.handlers import MongoHandler
import logging
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(MongoHandler.to(host=MONGO_URL, port=MONGO_PORT, db=MONGO_DATABASE, collection='log'))

