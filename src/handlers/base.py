#!/usr/bin/env python
# -*- coding: utf-8 -

#import tornado.httpserver
import traceback
from tornado.web import HTTPError
from tornado.web import RequestHandler
#from config import IMEI_BLACK_LIST
import logging
import json
import time
import sys
import hashlib
import hmac
import base64
from urlparse import urlparse
import functools

from db.account import Account

API_VERSION = "1.0"
API_PREFIX = "/" + API_VERSION

PROFILER = True
#PROFILER = False
if sys.platform == "win32":
    profiler_timer = time.clock     # On Windows, the best timer is time.clock()
else:
    profiler_timer = time.time      # On most other platforms the best timer is time.time()


class BaseHandler(RequestHandler):
    API_PREFIX = API_PREFIX
    """
    Точка входа для всех WEB-клиентов
    TODO! Необходима авторизация по cookcie
    """
    required = ()

    '''
    def initialize(self, *args, **kwargs):
        logging.info('** BaseHandler.initialize(%s, %s, %s)', repr(args), repr(kwargs), repr(self.request.arguments))
        logging.info(" == request:%s method=%s", repr(self.request), self.request.method)
    '''

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
        self.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Requested-With, Content-Length')
        self.set_header('Access-Control-Allow-Methods', 'OPTIONS, HEAD, GET, POST, PUT, DELETE')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def options(self, *args, **kwargs):
        pass

    def write_error(self, status_code, **kwargs):
        #print 'In get_error_html. status_code: ', status_code

        if 'exc_info' in kwargs:
            exc = kwargs['exc_info'][1]
            tracebacks = []
            if isinstance(exc, HTTPError):
                message = exc.log_message % exc.args
            else:
                message = str(exc)
            #kwargs["limit"] = 10
            for line in traceback.format_exception(*kwargs["exc_info"]):
                for l in line.split("\n"):
                    tracebacks.append(l)
            self.finish(json.dumps({
                "status_code": status_code,
                "message": message,
                "__tracebacks__": tracebacks
            }, indent=4) + "\r\n")
        else:
            super(BaseHandler, self).write_error(self, status_code, **kwargs)

    def prepare(self):
        #args = [self.decode_argument(arg) for arg in args]
        #kwargs = dict((k, self.decode_argument(v, name=k)) for (k, v) in kwargs.iteritems())
        #logging.info('** BaseHandler.prepare(%s, %s, %s)', repr(args), repr(kwargs), repr(self.request.arguments))
        domain = self.request.headers.get('Origin', None)
        if domain is None:
            domain = self.request.headers.get('Referer', None)
            if domain is None:
                domain = self.get_argument("domain", None)
                if domain is None:
                    domain = 'default'
        self.domain = urlparse(domain).netloc.split(':')[0].replace('.', '_').replace('$', '_')

        if self.request.method == 'POST':
            '''
                AngularJS по умолчанию использует Content-Type: application/json для POST-передачи
            '''
            if 'Content-Type' in self.request.headers:
                if "application/json" in self.request.headers['Content-Type']:
                    payload = self.request.body
                    logging.info('==payload:%s', payload)
                    try:
                        paydata = json.loads(payload)
                    except ValueError:
                        #raise tornado.httpserver._BadRequestException(
                        raise HTTPError(400, "Problems parsing JSON")
                    if type(paydata) != dict:
                        #raise tornado.httpserver._BadRequestException(
                        raise HTTPError(400, "JSON only accept key value objects")
                    logging.info('==paydata:%s', paydata)
                    for k, v in paydata.iteritems():
                        self.request.arguments[k] = v

        hash = hmac.new(self.application.settings["cookie_secret"], digestmod=hashlib.sha1)
        hash.update(str(self.request.remote_ip))
        hash.update(self.request.headers.get("User-Agent", ""))
        hash.update(self.get_argument('id', ''))
        hash.update(self.domain)
        self.identity = base64.urlsafe_b64encode(hash.digest()).rstrip('=')
        #self.identity2 = hash.hexdigest()

        self.auth = False
        self.akey = None
        access_token = self.request.headers.get('Authorization', None)
        logging.info(' from_header = %s', access_token)
        if access_token is None:
            access_token = self.get_argument("access_token", None)
            logging.info(' from_argument = %s', access_token)
            if access_token is None:
                access_token = self.get_cookie('access_token', None)
                logging.info(' from_cookie = %s', access_token)
        access_token = self.decode_signed_value("access_token", access_token)
        logging.info(' decoded value = %s', access_token)
        self.access_token = access_token
        if access_token is not None:
            akey, identity = access_token.split('@')
            if identity == self.identity:
                logging.info(' Identity is ok (%s)', identity)
                self.auth = True
                self.akey = akey
            else:
                logging.info(' Wrong identity %s != %s', identity, self.identity)

        '''
        if 'akey' in kwargs:
            self.account = Account.get(kwargs.pop("akey"), cached=True)
            # TODO! Check for self.domain == domain
            if self.account.isNone:
                raise json.dumps({
                    "error": "no account",
                    "akey": None,
                    "account": None
                })
        '''

    def writeasjson(self, data):
        if PROFILER:
            data['__profiler__'] = {
                'request': {
                    'method': self.request.method
                },
                'duration': self.request.request_time()
            }

        self.finish(json.dumps(data, indent=4))

    @staticmethod
    def auth(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.auth or self.akey is None:
                raise HTTPError(401, "Requires authentication")
            self.account = Account.get(self.akey, cached=True)
            if self.account is None:
                '''
                self.writeasjson({
                    "akey": None,
                    "account": None,
                })
                '''
                raise HTTPError(401, "Account not found")

            method(self, *args, **kwargs)
        return wrapper

    #def identity(self):
    #    pass

    '''
    def post(self, *args, **kwargs):
        self.write(json.dumps(self.apipost(*args, **kwargs), indent=4))

    def get(self, *args, **kwargs):
        if PROFILER:
            start = profiler_timer()

        answ = self.apiget(*args, **kwargs)

        if PROFILER:
            stop = profiler_timer()
            answ['profiler'] = {
                'kwargs': repr(kwargs),
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
    '''
    def decode_signed_value(self, name, value):
        from tornado.web import decode_signed_value
        return decode_signed_value(self.application.settings["cookie_secret"],
                                   name, value, max_age_days=31)
