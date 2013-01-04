#!/usr/bin/env python
# -*- coding: utf-8 -
__version__ = '0.1'
all = ['bingps']

from pymongo import Connection

print 'db:__init__.py'


class DB(object):
    def __init__(self, url='localhost', db='newgps_navicc'):
        self.connection = Connection(url)
        self.db = self.connection[db]

    def __del__(self):
        pass

    def collection(self, name):
        return self.db[name]
