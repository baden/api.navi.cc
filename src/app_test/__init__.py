# -*- coding: utf-8 -*-
import unittest

__author__ = 'maxaon'


class TestS(unittest.TestSuite):
    pass


if __name__ == "__main__":
    from application.controllers.systems import PointsControllerTest

    a = PointsControllerTest(methodName="test_get")
    a.run()
