# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from pymongo import MongoClient
from configs import Config
from libraries.acl import RBAC
from libraries.database import BaseCollection, Database
from libraries.web import RestHandler, RestError, UNAUTHORIZED, FORBIDDEN

__author__ = 'maxaon'


class NewHandler(RestHandler):
    _collection = TestCollection

    def get(self, id, *args, **kwargs):
        return self.collection.find({"_id": id})


class TestCollection(BaseCollection):
    _name = "test_collection_for_acl"

    def find(self, *args, **kwargs):
        self.is_allowed('test', 'get', args, kwargs)
        return super(TestCollection, self).find(*args, **kwargs)


    def __load_rbac(self, name):
        from yaml import safe_load

        basepath = os.path.dirname(__file__)
        name = os.path.abspath(os.path.join(basepath, 'rules', name + ".yaml"))
        c = safe_load(open(name))
        return c

    def assert_allowed(self, action, input_data):
        controller = 'test'
        rbac = RBAC(self.__load_rbac('rbac_in_collection'))
        roles = self.session.roles

        if not self.session.session_started:
            raise RestError(UNAUTHORIZED)

        if not rbac.isAllowed(roles, controller, action, input_data):
            raise RestError(FORBIDDEN)

    def is_allowed(self, resource, action, args, kwargs):
        rbac = RBAC(self.__load_rbac('rbac_in_collection'))
        fields = self.get_fields(args, kwargs)
        rbac.isAllowed(['simple_user'], resource, action, fields)

    def get_fields(self, args, kwargs):
        fields = []
        if len(args) > 1:
            spec = args[0]
        if len(args) > 2:
            fields = args[1]
        if 'spec' in kwargs:
            spec = kwargs['spec']
        if 'fields' in kwargs:
            fields = kwargs['fields']
        fields.extend(self.parse_spec(spec))

    def parse_spec(self, f):
        return f
        pass

    def parse_return_fields(self, f):
        return [k for k, v in f.iteritems() if int(v) == 1]

    def __parse_spec(self, spec):
        spec = {}

        for key, value in spec.iteritems():
            pass


    def update(self, spec, document, upsert=False, manipulate=False, safe=None, multi=False, check_keys=True,
               **kwargs):
        return super(TestCollection, self).update(spec, document, upsert, manipulate, safe, multi, check_keys,
                                                  **kwargs)


    def testTime(self, req_args, req_kwarg):
        """
        :param req_args: Requested arguments
        :param req_kwarg:
        """
        if len(req_args) > 1:
            spec = req_args[0]
        if len(req_args) > 2:
            fields = req_args[1]
            s
        if 'spec' in req_kwarg:
            spec = req_kwarg['spec']
        if 'fields' in req_kwarg:
            fields = req_kwarg['fields']


class TectAclInObjectCollection(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TectAclInObjectCollection, cls).setUpClass()
        config = Config.load("application.yaml", env='testing')
        client = MongoClient(**config.db)
        cls.db = TestCollection._db = Database(client, 'testCollection258')

    def testNew(self):
        since = 0
        till = 3600 * 24 * 7 * 31
        curs = self.collection.find({"imei": id, "hour": {"$gte": since // 3600, "$lte": till // 3600}})

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_collection(TestCollection._name)


if __name__ == "__main__":
    pass
