from __future__ import unicode_literals
import collections
import os
import unittest
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from libraries.acl import RBAC, RBACCollection
from libraries.database import BaseCollection, Database

__author__ = 'maxaon'
ALL_FIELDS = "$all"


class RuledCollection(object):
    '''
    **sort not controlled**
    '''

    _name = "somecol"
    user_roles = None

    def __init__(self, rbac):
        """
        :type rbac: RBAC
        :param rbac:
        """
        self._collection = BaseCollection(name=self._name)
        self._rbac = rbac

    def find(self, spec=None, fields=None, **kwargs):
        spec_fields = self.get_name_from_spec(spec) if spec else []
        return_fields = map(lambda t: t[0], filter(lambda field: field[1] >= 1, fields.iteritems())) if fields else []

        if not self._rbac.isAllowed(self.user_roles, self._name or self._collection.name, 'read',
                                    fields=spec_fields + return_fields):
            raise RBACNotAllowed()

        allowed_fields = self._rbac.getAllowedFields(self.user_roles, self._name or self._collection.name, 'read')

        remove_id, to_be_shown = None, None

        if fields is not None and "_id" in fields:
            remove_id = fields.get("_id")
            del fields["_id"]

        include = all(fields.values()) if fields is not None else True

        if ALL_FIELDS in allowed_fields:
            to_be_shown = fields or None
        else:
            if not fields:
                to_be_shown = allowed_fields
            elif include:
                to_be_shown = set(fields.keys()).intersection(allowed_fields)
            else:
                to_be_shown = set(allowed_fields).difference(fields.keys())
            to_be_shown = dict([(field, 1) for field in to_be_shown])
        if remove_id is not None:
            to_be_shown['_id'] = remove_id
        spec, fields, kwargs = self.ac_find_before_request(spec, fields, **kwargs)

        return self._collection.find(spec=spec, fields=to_be_shown, **kwargs)

    def ac_find_before_request(self, spec, fields, **kwargs):
        return spec, fields, kwargs

    def insert(self, doc_or_docs, manipulate=True, safe=None, check_keys=True, continue_on_error=False, **kwargs):

        docs = [doc_or_docs] if isinstance(doc_or_docs, dict) else doc_or_docs
        for doc in docs:
            fields = self.get_keys_from_insert(doc)
            if not self._rbac.isAllowed(self.user_roles, self._name or self._collection.name, 'create', fields):
                raise RBACError

        return self._collection.insert(doc_or_docs, manipulate, safe, check_keys, continue_on_error, **kwargs)

    def update(self, spec, document, upsert=False, manipulate=False, safe=None, multi=False, check_keys=True, **kwargs):
        spec_fields = self.get_name_from_spec(spec) if spec else []
        fields = self.get_keys_from_insert(document)
        if not self._rbac.isAllowed(self.user_roles, self._name or self._collection.name, 'update',
                                    fields + spec_fields):
            raise RBACError

        return self._collection.update(spec, document, upsert, manipulate, safe, multi,
                                       check_keys, **kwargs)

    def remove(self, spec_or_id=None, safe=None, **kwargs):

        if spec_or_id is None:
            spec_or_id = {}
        if not isinstance(spec_or_id, dict):
            spec_or_id = {"_id": spec_or_id}
        search_fields = self.get_name_from_spec(spec_or_id)
        if not self._rbac.isAllowed(self.user_roles, self._name or self._collection._name, 'delete', search_fields):
            raise RBACError()
        self._collection.remove(spec_or_id, safe, **kwargs)

    def get_name_from_spec(self, spec):
        names = []
        for k, v in spec.iteritems():
            if k.startswith("$"):

                if isinstance(v, dict):
                    raise RBACError("Dict was supplied. Spec=\n{}".format(spec))
                    # names.extend(self.get_name_from_spec(v))
                elif k == "$where":
                    raise NotImplementedError("Searching with '$where' not implemented by aclRules")

                elif isinstance(v, list) and (k == "$and" or k == "$or" or k == "$nor" or k == "$not"):
                    for list_elem in v:
                        names.extend(self.get_name_from_spec(list_elem))
                else:
                    raise RBACError("This exception newer should be raised")
            else:
                names.append(k)
        return names

    def get_keys_from_insert(self, doc):
        fields = []
        for k, v in doc.iteritems():
            if isinstance(v, dict):
                fields.extend(["{}.{}".format(k, sub_key) for sub_key in self.get_keys_from_insert(v)])
            else:
                fields.append(k)
        return fields


class ControllerWithMoneyRestriction(RuledCollection):
    def money_restriction(self, action, spec):
        g_rule, c_rule, a_rule = self._rbac.getFilterRules(self.user_roles, self._name or self._collection.name, action,
                                                           'money')
        rules = g_rule + c_rule + a_rule
        if not rules:
            return spec
        rules = [{"money": i} for i in rules]
        if spec:
            rules.append(spec)
        spec = {"$and": rules}
        return spec

    def ac_find_before_request(self, spec, fields, **kwargs):
        spec = self.money_restriction('read', spec)
        return spec, fields, kwargs


class ControllerWithAgeRestriction(RuledCollection):
    def age_restriction(self, action, spec):
        g_rule, c_rule, a_rule = self._rbac.getFilterRules(self.user_roles, self._name or self._collection.name, action,
                                                           'age')
        rules = g_rule + c_rule + a_rule
        if not rules:
            return spec

        rules = [{"age": i} for i in rules]
        if spec:
            rules.append(spec)
        spec = {"$and": rules}
        return spec

    def ac_find_before_request(self, spec, fields, **kwargs):
        spec = self.age_restriction('read', spec)
        return spec, fields, kwargs


class RBACError(Exception):
    pass


class RBACNotAllowed(RBACError):
    pass


class SomeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name = "test_db_222"
        BaseCollection._db = Database(MongoClient(), cls.db_name)

        cls.col = Collection(BaseCollection._db, RuledCollection._name)
        cls.col.remove()
        cls.col.insert([
            {"login": "aa", "password": "pass", "age": 22, "money": 100},
            {"login": "bb", "password": "pass", "age": 29, "money": 200},
            {"login": "cc", "password": "pass", "age": 39, "money": 500},
            {"login": "dd", "password": "pass", "age": 35, "money": 600},
            {"login": "ee", "password": "pass", "age": 17, "money": 0},
            {"login": "ff", "password": "pass", "age": 25, "money": 300}
        ])

    @classmethod
    def tearDownClass(cls):
        cls.col.remove()
        # return
        # BaseCollection._db.connection.drop_database(cls.db_name)


    def test_get_names_from_spec(self):
        c = RuledCollection(None)
        f = c.get_name_from_spec
        self.assertItemsEqual(f({"_id": 32}),
                              ['_id'])
        self.assertItemsEqual(f({"_id": 32, "login": "vasya"}),
                              ['_id', "login"])
        self.assertItemsEqual(f({"_id": 32, "age": {"$gte": 43}}),
                              ['_id', "age"])
        self.assertItemsEqual(f({"_id": 32, "age": {"$gte": 43}}),
                              ['_id', "age"])
        self.assertItemsEqual(f({"$and": [{"_id": 33}, {"login": "er"}]}),
                              ['_id', "login"])
        self.assertItemsEqual(f({
            "$and": [
                {"_id": 33},
                {"login": "er"},
                {"$or": [
                    {"pass": "green"},
                    {"role": {"$in": ["aa", "bb", "cc"]}}]}]}), ['_id', "login", "pass", "role"])

        with self.assertRaises(NotImplementedError):
            f({"$where": "1==1"})

        with self.assertRaises(RBACError):
            f({"$lt": {"kea": "sd"}})

    def assertResp(self, response, logins=None, fields=None):
        response = list(response)
        if logins is not None:
            resp_login = map(lambda r: r['login'], response)
            self.assertItemsEqual(resp_login, logins)
        if fields is not None:
            dic = collections.defaultdict(int)
            for i in response:
                for k in i:
                    dic[k] += 1
            self.assertItemsEqual(dic.keys(), fields)

    def test_find_simple(self):
        c = self.get_collection(RuledCollection, ['base_role'])
        self.assertResp(c.find(), ['aa', 'bb', 'cc', 'dd', 'ff', 'ee'], ['_id', 'login', 'age'])
        with self.assertRaises(RBACNotAllowed):
            self.assertResp(c.find({"money": 200}))
        self.assertResp(c.find({"login": 'aa'}), ['aa'])
        self.assertResp(c.find(fields={'money': 0}), fields=['_id', 'login', 'age'])
        self.assertResp(c.find(fields={'age': 0}), fields=['_id', 'login'])
        self.assertResp(c.find(fields={'_id': 0}), fields=['login', 'age'])
        self.assertResp(c.find(fields={'_id': 0, "login": 1}), fields=['login'])
        self.assertResp(c.find({"login": {"$in": ["aa", "bb"]}}, fields={'_id': 0, "login": 1}), fields=['login'],
                        logins=['aa', 'bb'])
        self.assertResp(c.find({"$and": [
            {"login": {"$in": ["aa", "bb"]}},
            {"age": {"$lt": 100}},
        ]}, fields={'_id': 0, "login": 1}), fields=['login'], logins=['aa', 'bb'])

        with self.assertRaises(RBACNotAllowed):
            c.find({"$and": [
                {"login": {"$in": ["aa", "bb"]}},
                {"age": {"$lt": 100}},
                {"money": {"$lt": 100}},
            ]})
        with self.assertRaises(RBACNotAllowed):
            c.find({"$and": [
                {"login": {"$in": ["aa", "bb"]}},
                {"age": {"$lt": 100}},
                {"$or": [{"money": {"$lt": 100}}, {"money": {"$gt": 100}}]},
            ]})

        self.assertResp(c.find({"$and": [
            {"login": {"$in": ["aa", "bb"]}},
            {"age": {"$lt": 100}},
            {"$or": [{"age": {"$lt": 26}}, {"age": {"$gt": 31}}]},
        ]}, {"_id": 0}), logins=['aa'], fields=['login', 'age'])

    def test_access_to_all(self):
        c = self.get_collection(RuledCollection, ['base_role', 'extended_role'])
        self.assertResp(c.find({"login": "aa"}), logins=['aa'], fields=['login', 'password', 'age', 'money', '_id'])
        self.assertResp(c.find({"login": "aa"}, {"money": 1, 'login': 1}), logins=['aa'],
                        fields=['money', '_id', 'login'])

    def test_class_with_money_limits(self):
        c = self.get_collection(ControllerWithMoneyRestriction, ['base_role', 'money_restriction'])
        self.assertResp(c.find(), ['dd'], ['_id', 'age', 'login'])
        self.assertResp(c.find({"login": "dd"}), ['dd'], ['_id', 'age', 'login'])
        self.assertResp(c.find({"age": {"$lt": 36}}), ['dd'], ['_id', 'age', 'login'])
        self.assertResp(c.find({"age": {"$lt": 25}}), [])

        with self.assertRaises(RBACError):
            self.assertResp(c.find({"money": {"$lt": 25}}), [])

    def test_class_with_age_limits(self):
        c = self.get_collection(ControllerWithAgeRestriction, ['base_role', 'age_restriction'])
        self.assertResp(c.find(), ['bb', 'cc', 'dd', 'ff'], ['_id', 'age', 'login'])
        self.assertResp(c.find({"age": {"$lt": 30}}), ['bb', 'ff'], ['_id', 'age', 'login'])
        self.assertResp(c.find({"login": "ee"}), [])

        with self.assertRaises(RBACNotAllowed):
            c.find({"money": {"$gt": 1}})

        with self.assertRaises(RBACError):
            self.assertResp(c.find({"money": {"$lt": 25}}), [])
        with self.assertRaises(RBACError):
            self.assertResp(c.find({"$and": [{"money": {"$lt": 25}}]}), [])

    def test_insert_and_delete(self):
        c = self.get_collection(RuledCollection, ['base_role'])
        created_obj = c.insert({"login": "hello", "age": 133})
        self.assertIn('_id', created_obj)
        self.assertIsInstance(created_obj['_id'], ObjectId)

        self.assertResp(c.find({"_id": created_obj['_id']}), ["hello"], ["_id", "age", "login"])

        c.remove(created_obj['_id'])
        self.assertResp(c.find({"_id": created_obj['_id']}), [])

        created_obj = c.insert({"login": "hello", "age": 133, "_id": "sa32"})
        self.assertResp(c.find({"_id": created_obj['_id']}), ["hello"], ["_id", "age", "login"])
        c.remove(created_obj['_id'])
        self.assertResp(c.find({"_id": created_obj['_id']}), [])

        with self.assertRaises(RBACNotAllowed):
            c.insert({'login'})


    def __load_rbac(self, name):
        from yaml import safe_load

        base_path = os.path.dirname(__file__)
        name = os.path.abspath(os.path.join(base_path, 'rules', name + ".yaml"))
        c = safe_load(open(name))
        return c

    def get_collection(self, coll_class, user_roles, name="collection_new"):
        """

        :param coll_class:
        :param user_roles:
        :param name:
        :return:
        :rtype: RuledCollection
        """
        rbac = RBACCollection(self.__load_rbac(name))
        c = coll_class(rbac=rbac)
        c.user_roles = user_roles
        return c

