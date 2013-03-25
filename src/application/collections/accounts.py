# -*- coding: utf-8 -*-
#from libs.web import RestHandler, RestRoute
#
#__author__ = 'maxaon'
#
#@RestRoute("/account")
#class Account(RestHandler):
#    def index(self):
#        return  {"message": "Hello world!"}
import random
from hashlib import sha1 as sha

from bson import SON

from libraries.database import BaseCollection, ActiveRecord


class Account(ActiveRecord):
    _collection = None
    _defaults = {'username': '', 'roles': ['user']}

    def isPasswordCorrect(self, password):
        return Account.hash_password(self.salt, password) == self.password

    @staticmethod
    def hash_password(salt, password):
        e = sha(salt)
        e.update(password)
        return e.hexdigest()

    @staticmethod
    def gen_salt():
        return sha(str(random.getrandbits(512))).hexdigest()

    @classmethod
    def create(cls, data):
        self = cls()
        for key, value in data.iteritems():
            if key == 'password':
                salt = Account.gen_salt()
                self['salt'] = salt
                self['password'] = Account.hash_password(salt, value)
            else:
                self[key] = value
        return self

    def update(self, other=None, **kwargs):
        if isinstance(other, (dict, SON)):
            if 'password' in other:
                salt = Account.gen_salt()
                other['salt'] = salt
                other['password'] = Account.hash_password(salt, other["password"])
        super(Account, self).update(other, **kwargs)


def model(m):
    def wrapper(cls):
        m._collection = cls
        return cls

    return wrapper


@model(Account)
class Accounts(BaseCollection):
    _name = "account"
    _model = Account


    @classmethod
    def authenticate(cls, login=None, password=None, group=None, email=None):
        """
        Authenticate user by (login or email),password and group
        :param cls: Class
        :param password: Account password
        :param group: Account group
        :param login: Account login
        :param email: Account email
        :return: ``Account`` if authentication is successful othervise  ``False``
        :rtype: Account bool
        """
        if password is None:
            raise ValueError('Password can\'t be empty')
        if not login and not email:
            raise ValueError("Authentication can't be without login or email")
        self = cls()
        query = {"login": login} if login else {"email": email}
        query.update({"group": group})

        account = self.find_one(query)
        if account and account.isPasswordCorrect(password):
            return account
        return False


    def insert(self, doc_or_docs, manipulate=True, safe=None, check_keys=True, continue_on_error=False, **kwargs):
        safe = True
        return super(Accounts, self).insert(doc_or_docs, manipulate, safe, check_keys, continue_on_error, **kwargs)







