# -*- coding: utf-8 -*-
import re
from application.collections.accounts import Account as AccountModel
from libraries.logger import LoggerMixin
from libraries.web import RestHandler, RestRoute, NOT_IMPLEMENTED, RestError, FORBIDDEN, METHOD_NOT_ALLOWED, RemoveItem, BaseRouter
from ..collections.accounts import Accounts as AccountsCollection


__author__ = 'maxaon'
RE_EMAIL = r"^[-a-z0-9!#$%&'*+/=?^_`{|}~]+(\.[-a-z0-9!#$%&'*+/=?^_`{|}~]+)*@([a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?\.)*(aero|arpa|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|pro|tel|travel|[a-z][a-z])$"
RE_LOGIN = r"[-a-z0-9!#$%&'*+/=?^_`{|}~]+(\.[-a-z0-9!#$%&'*+/=?^_`{|}~]+)*"
RE_GROUP = r"[a-z0-9]+(\.[-a-z0-9_]+)*"


@RestRoute()
class Accounts(RestHandler):
    _collection = AccountsCollection
    _actions_ = ['login', 'restore_password']
    _object_actions_ = []

    simple_filters = {}
    simple_filters['post'] = {
        "login": lambda key, value: value
        if value and len(value) >= 3 and len(value) <= 64 and re.match(RE_LOGIN, value, re.IGNORECASE)
        else RestError(400, "Login must be from 3 to 64 characters and have only -a-z0-9!#$%&'*+/=?^_`{|}~"),
        "password": 2,
        "email": lambda key, value: value if value and re.match(RE_EMAIL, value, re.IGNORECASE) else RestError(400,
                                                                                                               "Error email validation"),
        'group': lambda key, value: None if value == None else (value
                                                                if value and re.match(RE_GROUP,
                                                                                      value, re.IGNORECASE)
                                                                else RestError(
            "Group must start from letter or digit and contain only -a-z0-9_")),
        'name': 1
    }
    simple_filters['patch'] = {'login': 1, 'password': 1, 'email': 1}

    simple_filters['login'] = {'login': 2, 'password': 2, 'group': 1, }
    simple_filters['response'] = {'password': 0, 'salt': 0, '_id': lambda key, value: str(value)}


    def login(self, data, **kwargs):
        if not self.request.method.lower() == 'post': raise RestError(METHOD_NOT_ALLOWED)
        #        data = self.filter_params(kwargs, self.simple_filters['login'])

        account = AccountsCollection.authenticate(**data)

        if not account:
            raise RestError(FORBIDDEN, "Wrong login or password")
        self.session.start_session(True)
        self.session.set('login', account.login)
        self.session.set('account:oid', str(account._id))
        self.session.set('group', data.get('group'))
        account.update({"token": self.session.session_id})
        return account

    def post(self, data, *args, **kwargs):
        account = AccountModel.create(data)
        account.save()
        return  account

    def get(self, model, *args, **kwargs):
        return model

    def patch(self, model, data, *args, **kwargs):
        """
        :type model: application.collections.accounts.Account
        """
        model.update(data)
        model.save()
        return model


@RestRoute(route='/account{{action}}')
class Accountaaa(Accounts, LoggerMixin):
    _actions_ = []
    _object_actions_ = ['logout']

    def _get_id_and_action(self, *args, **kwargs):
        id = self.session.get('account:oid', None)
        if not id:
            self.logger.error("Access to account without session started")
            raise RestError(500)
        object_action = kwargs.get('action')
        if object_action and object_action.lower() in self._object_actions_: return id, object_action.lower()

        request_method = self.request.method.lower()
        return id, request_method


    def index(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def post(self, data, *args, **kwargs):
        raise RestError(METHOD_NOT_ALLOWED)

    def logout(self, **kwargs):
        raise self.session.close_session()


