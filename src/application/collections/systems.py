# -*- coding: utf-8 -*-
from time import time

from libraries.database import BaseCollection
from libraries.tools import DataConverter as Converter


__author__ = 'maxaon'


class Systems(BaseCollection):
    _name = "systems"
    pass


class Points1(BaseCollection):
    _name = "points1"


class PointsAggregated(object):
    RETURN_FORMAT_FLAT = 1
    RETURN_FORMAT_AGGREGATED = 2
    RETURN_FORMAT_FLAT_JSON = 3
    RETURN_FORMAT_AGGREGATED_JSON = 4

    _mongo_collection = Points1

    def __init__(self, redis, collection=None):
        if collection:
            self._mongo_collection = collection
        self.redis = redis
        super(PointsAggregated, self).__init__()

    @property
    def mongo_collection(self):
        """
        :rtype: BaseCollection
        :return: BaseCollection
        """
        if not isinstance(self._mongo_collection, BaseCollection):
            self._mongo_collection = self._mongo_collection()
        return self._mongo_collection

    def find(self, imei, since=None, till=None, return_format=RETURN_FORMAT_FLAT, fields=None):
        """
        Find point information defined by `imei` since `since` till `time`
        :param imei: IMEI for the point
        :param since: time (in seconds) since the data will be returned
        :param till: time (in seconds) since the data will be returned
        :param fields: returned fields (sing format data)
        :param return_format: return format for the field:
            * RETURN_FORMAT_FLAT
            * RETURN_FORMAT_AGGREGATED
            * RETURN_FORMAT_FLAT_JSON
            * RETURN_FORMAT_AGGREGATED_JSON
        :return: Normalized response in desired format
            """
        if since is None:
            till = time()
            since = till - 3600 * 24
        if till is None:
            till = since + 3600 * 24

        points = self.mongo_collection.find({"imei": imei, "hour": {"$gte": since // 3600, "$lte": till // 3600}},
                                            fields)
        # TODO add more precise time filtering
        points = list(points)
        curr_time = time()
        if curr_time - 3600 * 3 <= till: #about 3 hours
            hours_to_select = range(int(curr_time // 3600 - 3),
                                    int(1 + (till if till <= curr_time else curr_time) // 3600))
            # removing duplications
            hours_to_select = set(hours_to_select).difference([i["hour"] for i in points])
            points.extend(self._find_in_redis(imei, hours_to_select))
        return self._normalize_data(points, since=since, till=till, return_format=return_format, fields=fields)

    def find_last(self, imei, number_of_points=10, hour=None):
        """
        Find last points for `IMEI` for the `hour` (current by default)
        :param imei: IMEI the tracker
        :param number_of_points: Number of points (default = 10)
        :param hour: Time for which information gathered (default is current time) (looks only in redis)
        :return: last points or empty list
        """

        if hour is not None and time() // 3600 - hour > 2:
            raise NotImplementedError("Retrieving data from mongo not implemented")
        elif hour is not None:
            hour = int(hour)
        else:
            hour = time() // 3600

        number_of_points = int(number_of_points)

        if time() - hour * 3600 < 60 * 5:  # new hour just started
            pipe = self.redis.pipeline()
            pipe.lrange(self._format_key(imei, hour), number_of_points * -1, -1)
            pipe.lrange(self._format_key(imei, hour - 1), number_of_points * -1, -1)
            result = []
            points_raw = (result[0] + result[1])[0:number_of_points]
        else:
            points_raw = self.redis.lrange(self._format_key(imei, hour), number_of_points * -1, -1)
        return map(self.parse_bin_format, points_raw)

    def _normalize_data(self, data, return_format, since=None, till=None, fields=None):
        """
        Normalize data defined by `return_format` field from mongo db and redis db
        :param data: Received data from mongo and redis
        :param return_format: Return format
        :param since: Additional filter for flat formats
        :param till: Additional filter for flat formats
        :param fields: Returned fields
        :return: List of the point information
        """
        # TODO implement conversion
        if return_format == self.RETURN_FORMAT_FLAT:
            return data
        else:
            return data

    def _find_in_redis(self, imei, hours):
        """
        Retrieve information from redis using pipes(no transactions)

        :param imei: Pointer IMEI
        :type hours: list
        :param hours: Hours for which lookup is applied
        :return: List of points
        """
        if isinstance(hours, (int, long, float)):
            hours = [int(hours)]
        pipe = self.redis.pipeline(transaction=False)
        hours = map(int, hours)
        for hour in hours:
            pipe.lrange(self._format_key(imei, hour), 0, -1)
        result = []
        for hour, response in zip(hours, pipe.execute()):
            if response:
                result.append({"imei": imei, "hour": hour, "data": map(self.parse_bin_format, response)})
        return result

    def parse_bin_format(self, value):
        """
        Converts redis bin format to redis format
        :param value: Binary value from redis
        :return: dict from mongo
        """
        # TODO write converter class


        return Converter.to_dict(value)

    def _format_key(self, imei, hour):
        """
        Generate key name for redis
        :param imei: IMEI
        :param hour: Hour
        :return: key name
        """
        return "{}:{}".format(imei, int(hour))


class Points2(BaseCollection):
    _name = "points2"


class Points3(BaseCollection):
    _name = "points3"


class Points4(BaseCollection):
    _name = "points4"


if __name__ == "__main__":
    pass

