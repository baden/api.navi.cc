#!/usr/bin/env python
# -*- coding: utf-8 -


MONGO_URL = "mongodb://badenmongodb:1q2w3e@ds033257.mongolab.com:33257/baden_test"
MONGO_PORT = 33257
MONGO_DATABASE = "baden_test"

IMEI_BLACK_LIST = ('test-BLACK', 'test-BLACK2')
USE_BACKUP = True

# Сюда мы подключимся чтобы передавать сообщения клиентам через zmq
PUBLISHER_SUB = "ipc:///tmp/ws_sub"

# Redis URL
REDIS_SOCKET_PATH = "/tmp/redis.sock"
