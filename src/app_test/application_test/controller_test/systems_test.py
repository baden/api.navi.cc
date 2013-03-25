# -*- coding: utf-8 -*-
from  __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from app_test.application_test import AsyncHTTPTestCase

__author__ = 'maxaon'

#import tests
#print(tests.__file__)


class PointsControllerTest(AsyncHTTPTestCase):
    def test_get(self):
        response = self.fetch("/systems/10/points?since=0")
        ra = response


if __name__ == "__main__":
    pass
