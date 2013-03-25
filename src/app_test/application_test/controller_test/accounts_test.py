from __future__ import unicode_literals, absolute_import, division, generators, nested_scopes, print_function, with_statement

__author__ = 'maxaon'

import unittest
from app_test.application_test import *


class MyTestCase(AsyncHTTPTestCase):
    def test_something(self):
        req = JsonHTTPRequest("/accounts/", method="POST")
        req.method = POST
        cred = dict()
        cred['username'] = self.rand('some_user')
        cred['password'] = self.rand('password')
        cred['password'] = self.rand('title hello ' + self.inter)
        self.cred = cred.copy()
        req.rb = cred.copy()

        response = self.fetch(req)
        response.rethrow()

        self.assertResponseCode(200)


    def rand(self, prefix="", start=1000000, end=9999999):
        import random

        return prefix + str(random.randint(start, end))


if __name__ == '__main__':
    unittest.main()
