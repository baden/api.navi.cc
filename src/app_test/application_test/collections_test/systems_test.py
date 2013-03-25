# -*- coding: utf-8 -*-
from time import time
from unittest import TestCase
from bson.son import SON
from pymongo import MongoClient, uri_parser
from redis import Redis
from application.collections.systems import Points1, PointsAggregated
from configs import Config
from libraries import database
from libraries.database import BaseCollection


__author__ = 'maxaon'


class PointsAggregatedTest(TestCase):
    @classmethod
    def setUpClass(cls):
        conf = Config.load('application.yaml', 'testing', 'application-personal.yaml')

        cls.bootstrap_db(**conf.get("db", {}))

        cls.mongo_collection = Points1(cls.db, 'test148_' + str(cls.__name__))
        cls.mongo_collection.insert([
            {"imei": "33434", "hour": int(time() // 3600 - 4),
             "data": cls._gen_false_data(100, (time() // 3600 - 4) * 3600)},
            {"imei": "33434", "hour": int(time() // 3600 - 3),
             "data": cls._gen_false_data(100, (time() // 3600 - 3) * 3600)},
            {"imei": "33434", "hour": int(time() // 3600 - 2),
             "data": cls._gen_false_data(100, (time() // 3600 - 2) * 3600)},
            {"imei": "33434", "hour": int(time() // 3600 - 1),
             "data": cls._gen_false_data(100, (time() // 3600 - 1) * 3600)},
        ])
        cls.redis = Redis(**conf['redis'])
        cls.redis.rpush("33434:" + str(int(time() // 3600)), *cls._gen_false_data(100, (time() // 3600) * 3600))

    @classmethod
    def tearDownClass(cls):
        cls.mongo_collection.drop()
        cls.redis.delete("33434:" + str(int(time() // 3600)))

    @classmethod
    def bootstrap_db(cls, **params):
        db_name = params.get('name')
        del params['name']
        if not db_name:
            res = uri_parser.parse_uri(params['host'])
            db_name = res['database']
        cls.db = database.Database(MongoClient(**params), db_name)
        BaseCollection._db = cls.db

    @staticmethod
    def _gen_false_data(count, start_time):
        data = []
        step = 3600.0 / count
        from json import dumps

        for i in range(count):
            data.append(dumps(
                {"course": 256.0, "fsource": 8, "sats": 6,
                 "photo": 0,
                 "vout": 12, "time": start_time + i * step,
                 "lat": 50.518,
                 "speed": 92.2 + i,
                 "lon": 42.4783,
                 "vin": 42}
            ))
        return data

    def test_find(self):
        ta = PointsAggregated(self.redis, self.mongo_collection)
        points = ta.find("33434")
        self.assertEqual(len(points), 5)
        points = ta.find("33434", int(time() // 3600 - 3) * 3600)
        self.assertEqual(len(points), 4)
        points = ta.find("33434", int(time() // 3600 - 3) * 3600, int(time() // 3600 - 3) * 3600)
        self.assertEqual(len(points), 1)

    def test_find_last(self):
        ta = PointsAggregated(self.redis, self.mongo_collection)
        points = ta.find_last("33434")
        self.assertIsInstance(points, list)
        self.assertEqual(len(points), 10)
        self.assertIsInstance(points[0], (dict, SON))

        points = ta.find_last("33434", 25)
        self.assertEqual(len(points), 25)

        points = ta.find_last("33434", hour=123)
        self.assertIsInstance(points, list)
        self.assertEqual(len(points), 0)


if __name__ == "__main__":
    pass
