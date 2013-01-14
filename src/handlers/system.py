# -*- coding: utf-8 -*-

from route import Route
from base import BaseHandler
from db.system import System


#@Route(r"/api/account/systems/del/(?P<akey>[^\/]+)/(?P<skey>[^\/]+)")
@Route(BaseHandler.API_PREFIX + r"/system/changedesc/(?P<skey>[^\/]+)")
class SystemChangeDesc(BaseHandler):
    def get(self, skey):
        #skey = self.get_argument("skey", "=")
        desc = self.get_argument("desc", "Internal error")
        '''
        # TODO! Добавить проверку на право просмотра
        akey = self.get_argument("akey", "")
        domain = Account.get_domain(akey)
        #account = Account.filter(self.application.account.get(akey))

        self.application.system.get(skey)
        '''

        #domain = self.request.host.split(':')[0]

        System().change_desc(skey, desc, domain=self.domain)

        self.writeasjson({
            "result": "not_implemented_yet",
            "skey": skey,
            "domain": self.domain,
            "request": {
                "dir": dir(self.request),
                "connection": {
                    "dir": dir(self.request.connection),
                    "address": self.request.connection.address,
                    "xheaders": self.request.connection.xheaders
                },
                "headers": repr(self.request.headers),
                "uri": str(self.request.uri),
                "full_url": str(self.request.full_url),
                "path": str(self.request.path),
                "host": str(self.request.host)
            }
        })
