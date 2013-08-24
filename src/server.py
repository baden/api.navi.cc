#!/usr/bin/env python
# -*- coding: utf-8 -

from publisher import Publisher
#from publisher import publisher

import os
"""
here = os.path.dirname(os.path.abspath(__file__))
os.environ['PYTHON_EGG_CACHE'] = os.path.join(here, '..', 'misc/virtenv/lib/python2.7/site-packages')
virtualenv = os.path.join(here, '..', 'misc/virtenv/bin/activate_this.py')
execfile(virtualenv, dict(__file__=virtualenv))

# Control in head
import sys
sys.path.append("../misc/virtenv/lib/python2.7/site-packages")

print("virtualenv=", repr(virtualenv))
"""
import tornado.options
#import tornado.ioloop
from tornado.ioloop import IOLoop
import tornado.web
import platform
#import pymongo
import time
from datetime import datetime

#from time import sleep
#import signal
#import logger
from config import *


from mongolog.handlers import MongoHandler
import logging
logging.getLogger().setLevel(logging.DEBUG)
# logging.getLogger().addHandler(MongoHandler.to(host=MONGO_URL, port=MONGO_PORT, db=MONGO_DATABASE, collection=LOG_COLLECTION))


#from db import DB
#from db.account import Account
#from db.system import System
#from db.bingps import BinGPS
#from db.logs import Logs


#from handlers import *
from handlers.route import Route
from handlers import *
#from handlers import bingps

import logging


publisher = Publisher()


#push_socket.send_pyobj(msg)
#logging.getLogger().setLevel(logging.DEBUG)
#log = logging.getLogger('tornado.general')
#log.setLevel(logging.DEBUG)
#log.addHandler(MongoHandler.to(host='mongodb://badenmongodb:1q2w3e@ds033257.mongolab.com:33257/baden_test', port=33257, db='baden_test', collection='log'))

#log = logging.getLogger('demo')
#log.setLevel(logging.DEBUG)

#db = DB(url=MONGO_URL, db=MONGO_DATABASE)
#dblog = db.collection("log")
#dblog.ensure


#fake = db.collection("fake")

#redis = Redis(unix_socket_path=REDIS_SOCKET_PATH)

inmemcounter = 0
startedat = datetime.utcnow()


#account = Account(db, redis)
#system = System(db, redis)


def delta2dict(delta):
    """return dictionary of delta"""
    return {
        'year': delta.days / 365,
        'day': delta.days % 365,
        'hour': delta.seconds / 3600,
        'minute': (delta.seconds / 60) % 60,
        'second': delta.seconds % 60,
        'microsecond': delta.microseconds
    }


def delta2human(delta, precision=2):
    """return human readable delta string"""
    units = ('year', 'day', 'hour', 'minute', 'second')
    d = delta2dict(delta)
    hlist = []
    count = 0
    for unit in units:
        if count >= precision:
            break           # met precision
        if d[unit] == 0:
            continue        # skip 0's
        s = '' if d[unit] == 1 else 's'   # handle plurals
        hlist.append('%s %s%s' % (d[unit], unit, s))
        count += 1
    return ', '.join(hlist)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global inmemcounter, startedat
        inmemcounter += 1
        self.set_header("Cache-control", "no-cache")
        self.write("<h2>API_newgps_navi_cc server</h2><ul>")

        self.write("<li><b>Server work time:</b> %s</li>" % delta2human(datetime.utcnow() - startedat))
        self.write("<li><b>Global counter:</b> %d</li>" % inmemcounter)

        # fall = fake.find_one({"_id": "counter"})
        # if fall is None:
        #     fall = {"_id": "counter", "value": 0}
        # else:
        #     fall["value"] += 1
        # self.write("<li><b>Mongo counter:</b> %s</li>" % repr(fall["value"]))
        # fake.save(fall)

        self.write("</ul><h2>Platform information</h2><ul>")
        self.write("<li><b>System:</b> %s</li>" % platform.system())
        self.write("<li><b>Process ID:</b> %s</li>" % str(os.getpid()))
        self.write("<li><b>Release:</b> %s</li>" % platform.release())
        self.write("<li><b>Version:</b> %s</li>" % platform.version())
        self.write("<li><b>Machine:</b> %s</li>" % platform.machine())
        self.write("<li><b>Processor:</b> %s</li>" % platform.processor())
        self.write("<li><b>Node:</b> %s</li>" % platform.node())
        self.write("<li><b>Python:</b> %s</li>" % platform.python_version())

        self.write("</ul><h2>Memory information</h2><ul>")
        for m in open('/proc/meminfo'):
            self.write("<li>%s</li>" % m)

        self.write("</ul>")


#bingps = BinGPS(db)
#logs = Logs(db)


class MyApplication(tornado.web.Application):
    #db = db
    publisher = publisher
    #bingps = bingps
    #account = account
    #system = system
    #logs = logs
    #dblog = dblog
    """
    def log_request(self, handler):

        if handler.get_status() < 400:
            log_method = log.info
        elif handler.get_status() < 500:
            log_method = log.warn
        else:
            log_method = log.error

        request_time = 1000.0 * handler.request.request_time()
        log_message = '%d %s %.2fms' % (handler.get_status(), handler._request_summary(), request_time)
        log_method(log_message)
        #print ' LOG:%s' % log_message
    """

logging.info("Routes=%s", repr([(r.name, r.regex.pattern) for r in Route.routes()]))

settings = {
    #"xsrf_cookies": True,
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "debug": True
}

#application = tornado.web.Application([
application = MyApplication([
    (r"/", MainHandler),
    #(r"/bingps", handlers.bingps.BinGps, dict(publisher=publisher, bingps=bingps, system=system)),
    #(r'/addlog.*', addlog.AddLog, dict(publisher=publisher, system=system)),    # События
    #(r'/config.*', config.Config, dict(publisher=publisher, system=system)),    # Конфигурация системы
    #(r'/params.*', config.Params, dict(publisher=publisher, system=system)),    # Запрос параметров системы, например localhost/params?cmd=check&imei=353358019726996
    #(r'/inform.*', point.main.Inform'),
    #(r'/ping.*', 'point.main.Ping'),
    #(r'/firmware.*', 'point.main.Firmware'),

    #(r"/logs", handlers.logs.Logs, dict(dblog=dblog)),
] + Route.routes(), **settings)


#tornado.web.Application.log_request = MongoHandler

#print repr(application.log_request)
#application.log_request = MongoHandler.to(host='mongodb://badenmongodb:1q2w3e@ds033257.mongolab.com:33257/baden_test', port=33257, db='baden_test', collection='log')
#application.log_request = MongoHandler
#.to(host='mongodb://badenmongodb:1q2w3e@ds033257.mongolab.com:33257/baden_test', port=33257, db='baden_test', collection='log')


#log.debug('Start point.navi.cc server.')
#tornado.options.parse_command_line()
'''
    log.debug("1 - debug message")
    log.info("2 - info message")
    log.warn("3 - warn message")
    log.error("4 - error message")
    log.critical("5 - critical message")
'''


def sig_handler(sig, frame):
    """Catch signal and init callback.

    More information about signal processing for graceful stoping
    Tornado server you can find here:
    http://codemehanika.org/blog/2011-10-28-graceful-stop-tornado.html
    """
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)


def shutdown():
    """Stop server and add callback to stop i/o loop"""
    io_loop = IOLoop.instance()

    #logging.info('Stopping server')
    #io_loop.stop()
    # Can add some stop tasks here.

    logging.info('Will shutdown in 1 seconds ...')
    io_loop.add_timeout(time.time() + 1, io_loop.stop)


def main():
    logging.info("starting torando web server")

    #signal.signal(signal.SIGTERM, sig_handler)
    #signal.signal(signal.SIGINT, sig_handler)

    address = os.environ.get('INTERNAL_IP', '0.0.0.0')
    port = int(os.environ.get('INTERNAL_POINT_PORT', '8182'))
    application.listen(port, address=address)
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        IOLoop.instance().stop()
        #io_loop.stop()
        logging.info('Exit application')
    publish_stream.close()


if __name__ == '__main__':
    tornado.options.parse_command_line()
    main()
