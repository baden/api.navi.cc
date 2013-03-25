# -*- coding: utf-8 -*-
from json import loads

from tornado.httpclient import HTTPResponse

from app_test.application_test import AsyncHTTPTestCase


__author__ = 'maxaon'


class PointsTest(AsyncHTTPTestCase):
    def test_select(self):
        response = self.fetch("/systems/10/points?since=0")
        assert isinstance(response, HTTPResponse)
        self.assertGreater(int(response.headers.get("X-Number-of-points")), 0)
        self.assertLess(response.request_time, 5)
        b = loads(response.body)

    def fetch(self, path, **kwargs):
        self.http_client.fetch(self.get_url(path), self.stop, **kwargs)
        return self.wait(timeout=None)


if __name__ == "__main__":
    pass
