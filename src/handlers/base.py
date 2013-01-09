#!/usr/bin/env python
# -*- coding: utf-8 -

from tornado.web import RequestHandler
#from config import IMEI_BLACK_LIST
import logging
import json
import time
import sys
from urlparse import urlparse


PROFILER = True
#PROFILER = False
if sys.platform == "win32":
    profiler_timer = time.clock     # On Windows, the best timer is time.clock()
else:
    profiler_timer = time.time      # On most other platforms the best timer is time.time()


class BaseHandler(RequestHandler):
    """
    Точка входа для всех WEB-клиентов
    TODO! Необходима авторизация по cookcie
    """
    required = ()

    def options(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With, Content-Length')

    def post(self, *args, **kwargs):
        '''
            AngularJS использует Content-Type: application/json для POST-передачи
            Этот тип наиболее удобен для передачи массивов,
            поэтому необходимо использовать его при выборе другого фреймфорка
        '''
        if 'Content-Type' in self.request.headers:
            if "application/json" in self.request.headers['Content-Type']:
                payload = self.request.body
                #logging.info('==payload:%s', payload)
                paydata = json.loads(payload)
                #logging.info('==paydata:%s', paydata)
                for k, v in paydata.iteritems():
                    self.request.arguments[k] = v

        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json; charset=utf-8')

        self.domain = urlparse(self.request.headers.get('Origin', '')).netloc

        self.write(json.dumps(self.apipost(*args, **kwargs), indent=4))

    def get(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        #self.set_header('Content-Type', 'application/octet-stream')

        # Для определения
        domain = self.request.headers.get('Origin', None)
        if domain is None:
            domain = self.request.headers.get('Referer', None)
            if domain is None:
                domain = self.get_argument("domain", None)
                if domain is None:
                    domain = 'default'
        self.domain = urlparse(domain).netloc.split(':')[0].replace('.', '_').replace('$', '_')

        callback = self.get_argument('callback', None)
        if PROFILER:
            start = profiler_timer()

        answ = self.apiget(*args, **kwargs)

        if PROFILER:
            stop = profiler_timer()
            answ['profiler'] = {
                'start': start,
                'stop': stop,
                'duration': int((stop - start) * 1000000.0),
                'duration_item': 'us'
            }
        if callback is not None:
            self.write(callback + "(" + json.dumps(answ, indent=4) + ");")
        else:
            self.write(json.dumps(answ, indent=4))

    def apipost(self, *args, **kwargs):
        pass

    def apiget(self, *args, **kwargs):
        pass

