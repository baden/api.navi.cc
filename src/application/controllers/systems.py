# -*- coding: utf-8 -*-
import application.collections.systems as collections
from libraries.web import RestHandler

__author__ = 'maxaon'

if __name__ == "__main__":
    pass

class SystemsController(RestHandler):
    _collection = collections.Systems

    def get(self, id, *args, **kwargs):
        return self.get_model(id)

    def post(self, data, *args, **kwargs):
        self.collection.insert(data)

    def patch(self, id, data, *args, **kwargs):
        self.collection.update(id, data)

    def delete(self, id, *args, **kwargs):
        self.collection.remove(id)





