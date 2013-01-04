#!/usr/bin/env python
# -*- coding: utf-8 -

#from bisect import insort


class BinGPS(object):
    def __init__(self, db):
        self.col = db.collection("bingps")
        self.col.ensure_index([
            ("skey", 1), ("hour", 1)
        ])

    def update(self, *args):
        self.col.update(*args)


class Packer(object):
    def __init__(self):
        self.packet = {}    # Тут будут складываться точки по часам

    def add(self, point):
        hour = int(point['time'] // 3600)
        if hour not in self.packet:
            self.packet[hour] = []
        #insort(self.packet[hour].append(point)
        self.packet[hour].append(point)

    def save(self, collection, skey):
        # TODO! Batch operations
        for hour, data in self.packet.iteritems():
            for packet in data:
                collection.update({'skey': skey, 'hour': hour}, {"$push": {"data": packet}}, True)
