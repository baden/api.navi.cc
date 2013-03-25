# -*- coding: utf-8 -*-
from collections import deque
import time

from tornado.web import asynchronous
import dateutil.parser as dp

import application.collections.systems as collections
from libraries.logger import LoggerMixin
from libraries.web import RestHandler, RestRoute, RestError


__author__ = 'maxaon'

if __name__ == "__main__":
    pass


@RestRoute("/systems")
class SystemsController(RestHandler):
    _collection = collections.Systems

    def get(self, id, *args, **kwargs):
        return self.get_model(id)

    def post(self, data, *args, **kwargs):
        self.collection.insert(data)

    def patch(self, id, data, *args, **kwargs):
        self.collection.update(id, data)

    def delete(self, id, *args, **kwargs):
        self.collection.remove(id)


@RestRoute("/systems/{{id}}/points1")
class PointsController(RestHandler, LoggerMixin):
    _collection = collections.PointsAggregated
    DEFAULT_BATCH_SIZE = 2
    _actions_ = ["last_points"]

    def index(self, *args, **kwargs):
        pass

    def collection(self):
        """

        :rtype  : PointsAggregated
        :return :
        """
        return super(PointsController, self).collection()

    @asynchronous
    def get(self, id, *args, **kwargs):
        logger = self.logger.getChild('get')
        try:
            till = self._parse_date(kwargs.get("till"), time.time())
            since = self._parse_date(kwargs.get("since"), till - 86400)
        except ValueError:
            raise RestError("Unable to convert date")
        time_start = time.time()

        fields = kwargs.get('fields', [])
        if fields:
            if not isinstance(fields, list) and isinstance(fields, unicode):
                fields = fields.split(",")
            fields_mode = kwargs.get('fields_mode', 1)
            fields = dict([(f, fields_mode) for f in fields])
        else:
            fields = {}
        fields.update(_id=0)

        curs = self.collection.find(id, since, till, fields=fields)
        if kwargs.get("limit"):
            try:
                limit = int(kwargs.get("limit"))
                curs.limit(limit)
            except ValueError:
                raise RestError("Wrong limit type")
        try:
            per = int(kwargs.get('per', self.DEFAULT_BATCH_SIZE))
        except ValueError:
            raise RestError("Wrong type of 'per'")

        show_all = (per == -1)
        per = per if 100 <= per <= 3000 else self.DEFAULT_BATCH_SIZE
        time_for_first_chunk = time.time()
        number_of_points = 0
        number_of_points = curs.count()
        self.add_header("X-Number-of-points", number_of_points)
        if show_all:
            self.write_object(curs)
            self.flush()
            time_for_first_chunk = time.time()
            self.finish()
        else:
            curs.batch_size(per)
            self.write("[")
            docs = deque()
            #            i = 0
            #            while curs._refresh():
            #                self._write_partial_response(curs._data, "," if i != 0 else "")
            #                curs._data.clear()
            #                i=i+1
            #            self.logger.debug("before entering:{}".format((self.request._start_time - time.time()) * -1000))
            #            logger.info("befor entering {}".format((time.time() - time_start) * 1000))
            #            tc = time.time()
            for i, doc in enumerate(curs):
                if (i % per == 0) and i != 0:
                #                    logger.info("SELECT {}".format((time.time() - tc) * 1000))
                #                    tc = time.time()
                    self._write_partial_response(docs, ",")
                    #                    logger.info("Write {}".format((time.time() - tc) * 1000))
                    time_for_first_chunk = time.time()
                    docs.clear()
                docs.append(doc)
            if docs:
                self._write_partial_response(docs)
            self.write("]")
            self.flush()
            self.finish()
        logger.info(
            "First chunk is {} ms, all in {} ms for {} points".format((time.time() - time_for_first_chunk) * 1000,
                                                                      (time.time() - time_start) * 1000,
                                                                      number_of_points))
        #            self.logger.debug("Totalreq:{}".format((polt - time.time()) * -1000))
        #            self.logger.debug("Total:{}".format((t - time.time()) * -1000))

    def last(self, id, *args, **kwargs):
        return self.collection.get_last_points(id)

    def _write_partial_response(self, docs, post=""):
        t = time.time()
        data = self.dumps(docs)
        #        self.logger.debug("Time for dump:{}".format((t - time.time()) * -1000))
        t = time.time()
        self.write(data[1:-1] + post)
        #        self.logger.debug("Time for write:{}".format((t - time.time()) * -1000))
        t = time.time()
        self.flush()

    #        self.logger.debug("Time for flush:{}".format((t - time.time()) * -1000))

    def _parse_date(self, date, default=None):
        if not date:
            return default

        if date:
            try:
                date = int(date)

            except ValueError:
                date = dp.parse(date).time()
        return date


@RestRoute("/systems/{{id}}/points2")
class Points2(PointsController):
    _collection = collections.Points2
    DEFAULT_BATCH_SIZE = 100


@RestRoute("/systems/{{id}}/points3")
class Points3(PointsController):
    _collection = collections.Points3
    DEFAULT_BATCH_SIZE = 100


@RestRoute("/systems/{{id}}/points4")
class Points4(PointsController):
    _collection = collections.Points4

    def _write_partial_response(self, docs, post=""):
        r = deque()
        for doc in docs:
            r.append('{{"imei":"{imei}","hour":{hour},"data":{data}}}'.format(**doc))
        self.write(",".join(r) + post)

    DEFAULT_BATCH_SIZE = 2







