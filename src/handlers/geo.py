# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
# from db.system import System
from db.bingps import BinGPS
# from tornado.web import HTTPError

import logging
# from bson import Binary
from base64 import b64encode


@Route(BaseHandler.API_PREFIX + r"/geo/get/(?P<skey>[^\/]+)/(?P<dtfrom>[^\/]+)/(?P<dtto>[^\/]+)")
class GeoGet(BaseHandler):

    # schema = {}
    # schema["PATCH"] = {
    #     "title": "patch system",
    #     "type": "object",
    #     "properties": {
    #         "desc": {
    #             "type": "string",
    #             "required": True
    #         }
    #     },
    #     "additionalProperties": False
    # }

    # @BaseHandler.auth
    def get_old(self, skey, dtfrom, dtto):
        # System(skey).change_desc(self.payload["desc"], domain=self.domain)
        def join(blist):
            j = ""
            for b in blist:
                j += b
            return j

        data = BinGPS.getraw(skey, int(dtfrom), int(dtto))
        logging.info("data = %s" % repr(data))

        result = ({"hour": d["hour"], "data": b64encode(join(d["data"]))} for d in data)

        self.writeasjson({
            "skey": skey,
            "from": dtfrom,
            "to": dtto,
            "data": [r for r in result]
        })

    def get(self, skey, dtfrom, dtto):
        # System(skey).change_desc(self.payload["desc"], domain=self.domain)
        self.set_header('Content-Type', 'application/octet-stream')
        def join(blist):
            j = ""
            for b in blist:
                j += b
            return j

        data = BinGPS.getraw(skey, int(dtfrom), int(dtto))
        logging.info("data = %s" % repr(data))

        # result = ({"hour": d["hour"], "data": b64encode(join(d["data"]))} for d in data)

        for d in data:
            self.write(join(d["data"]))


@Route(BaseHandler.API_PREFIX + r"/geo/hours/(?P<skey>[^\/]+)/(?P<dtfrom>[^\/]+)/(?P<dtto>[^\/]+)")
class GeoHours(BaseHandler):
    def get(self, skey, dtfrom, dtto):

        data = BinGPS.gethours(skey, int(dtfrom), int(dtto))
        # data = [d for d in BinGPS.gethours(skey, int(dtfrom), int(dtto))]

        self.writeasjson({
            "skey": skey,
            "from": dtfrom,
            "to": dtto,
            "data": data["result"]
        })
