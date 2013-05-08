#!/usr/bin/env python
# -*- coding: utf-8 -

#from bisect import insort
from base import DBBase
import logging
from zlib import decompress

class BinGPS(DBBase):
    def __init__(self, *args, **kwargs):
        super(BinGPS, self).__init__(*args, **kwargs)
        # self.collection.ensure_index([
        #     ("skey", 1), ("hour", 1)
        # ])
        self.buffer = self.db[self.__class__.__name__ + "_buffer"]

    # @classmethod
    # def packer(cls, skey):
    #     bingps = cls()
    #     bingps.skey = skey
    #     bingps.packet = {}
    #     return bingps

    # def add_point_to_packer(self, point):
    #     hour = int(point['time'] // 3600)
    #     if hour not in self.packet:
    #         self.packet[hour] = []
    #     #insort(self.packet[hour].append(point)
    #     self.packet[hour].append(point)

    # def save_packer(self):
    #     # TODO! Batch operations
    #     logging.info('BinGPS.save_packer(%s)', self.skey)
    #     for hour, data in self.packet.iteritems():
    #         for packet in data:
    #             logging.info('BinGPS.save_packer.update(%s, %s)', self.skey, str(packet))
    #             self.collection.update({'skey': self.skey, 'hour': hour}, {"$push": {"data": packet}}, True)

    @classmethod
    def getraw(cls, skey, hourfrom, hourto):
        # TODO! Batch operations
        # logging.info('BinGPS.save_packer(%s)', self.skey)
        bingps = cls()
        bingps.skey = skey
        # bingps.packet = {}
        # return bingps.collection.find({'skey': skey, 'hour': hourfrom}, {'_id': 0, 'skey': 0})
        # return bingps.collection.find({'skey': skey, 'hour': hourfrom}, {'hour': 1, 'data': 1, '_id': 0})

        data = ""
        # Данные из основной базы
        query = bingps.collection.find({'skey': skey, 'hour': {"$gte": hourfrom, "$lte": hourto}})
        for r in query:
            for d in r["data"]:
                data += decompress(d)

        # Данные из буффера
        query = bingps.buffer.find({'skey': skey, 'hour': {"$gte": hourfrom, "$lte": hourto}}).sort("_id", 1)
        for r in query:
            data += r["data"]

        return data
        # for hour, data in self.packet.iteritems():
            # self.collection.update({'skey': self.skey, 'hour': hour}, {"$push": {"data": Binary(data)}}, True)
            # for packet in data:
            #     # logging.info('BinGPS.save_packer.update(%s, %s)', self.skey, str(packet))
            #     # self.collection.update({'skey': self.skey, 'hour': hour}, {"$push": {"data": packet}}, True)

    @classmethod
    def gethours(cls, skey, hourfrom, hourto):
        bingps = cls()
        bingps.skey = skey
        # return bingps.collection.aggregate([
        #     {"$match": {"skey": skey}},
        #     {"$project": {"hour": 1}}
        # ])

        hours = []
        # Данные из основной базы
        query = bingps.collection.aggregate([
            {"$match": {"skey": skey, "hour": {"$gte": hourfrom, "$lte": hourto}}},
            # {"$project": {"hour": 1, "_id": 0}},      # Попробовать, имеет ли смысл фильтровать промежуточные данные
            {"$group": {"_id": 0, "hours": {"$addToSet": "$hour"}}},
            # {"$project": {"hours": 1, "_id": 0}}
        ])["result"]
        if len(query) > 0:
            hours.extend(query[0]["hours"])

        # Данные из буффера
        query = bingps.buffer.aggregate([
            {"$match": {"skey": skey, "hour": {"$gte": hourfrom, "$lte": hourto}}},
            # {"$project": {"hour": 1, "_id": 0}},      # Попробовать, имеет ли смысл фильтровать промежуточные данные
            {"$group": {"_id": 0, "hours": {"$addToSet": "$hour"}}},
            # {"$project": {"hours": 1, "_id": 0}}
        ])["result"]
        if len(query) > 0:
            hours.extend(query[0]["hours"])

        return hours
