from time import time
import unittest

from mock import MagicMock

from libraries.session import SessionManager, SessionError
from libraries.database import Redis


__author__ = 'maxaon'


class SessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #
        cls.redis = SessionManager._redis = Redis()
        cls.session_prefix = SessionManager.REDIS_PREFIX = "sess_test_redis" + str(time())

    def tearDown(self):
        self.assertEqual(len(self.redis.keys(self.session_prefix + "*")), 0, "Some keys leave in DB")

    def gen_handler_mock(self, sid=None):
        handler = MagicMock()
        handler.get_cookie = MagicMock(return_value=None)
        if sid is not None:
            handler.request.headers.get = MagicMock(return_value=sid)

        else:
            handler.request.headers.get = MagicMock(return_value=None)
            handler.settings.get = MagicMock(return_value={})
        return handler

    def test_session(self):
        # "a5198aa4-b3d7-418c-b48f-793fa2c9bd95"
        handler = self.gen_handler_mock()
        s = SessionManager(handler)

        with self.assertRaises(SessionError):
            s.set("some", "value")

        sid = s.start_session("some_user")
        self.assertRegexpMatches(sid, r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-z0-9]{12}")
        s.set("hello", "world")

        self.assertEqual("world", s.get('hello'))
        s.close_session()

    def test_between_requests(self):
        sess_manager = SessionManager(self.gen_handler_mock())
        sid = sess_manager.start_session("some_user_2")
        sess_manager.set("some", "value")
        sess_manager = SessionManager(self.gen_handler_mock(sid=sid))
        self.assertEqual(sess_manager.get("some"), "value")
        sess_manager.close_session()

    def test_delete(self):
        sess_manager = SessionManager(self.gen_handler_mock())
        sid = sess_manager.start_session("some_user_2")
        sess_manager.set("key", "value")
        self.assertTrue("value", sess_manager.get("key"))
        sess_manager.delete("key")
        self.assertIsNone(sess_manager.get("key"))
        sess_manager.close_session()

    def test_other_logout(self):
        sid1 = SessionManager().start_session("some_user")
        sid2 = SessionManager().start_session("some_user")
        sid3 = SessionManager().start_session("some_user")
        sess = SessionManager()
        sid_cur = sess.start_session("some_user")
        sess.set("my", "value")
        sess.close_other_session()

        self.assertEqual("value", sess.get("my"))
        self.assertTrue(sess.session_started)

        sess.close_session()
        sess1 = SessionManager(session_id=sid1)
        self.assertFalse(sess1.session_started)

    def test_malicious_content_session_id(self):

        with self.assertRaises(SessionError):
            SessionManager(session_id="eqwe")
        with self.assertRaises(SessionError):
            SessionManager(session_id="a5198aa4-b3d7-418c-b48f-793fa2c9bd95as")
        with self.assertRaises(SessionError):
            SessionManager(session_id="a5198aa4-b3d7-418c-b48f-793fa2c9bz95")
        with self.assertRaises(SessionError):
            SessionManager(session_id="a5198aa4-b3d7-418c-b48fs793fa2c9bd95")
        with self.assertRaises(SessionError):
            SessionManager(session_id="a5198aa4-b3d7-418c-b48f-793fa2c9bd95\n2")
        with self.assertRaises(SessionError):
            SessionManager(session_id="a5198aa4-b3d7-418c-b48f\000793fa2c9bd95")

        with self.assertRaises(SessionError):
            SessionManager(self.gen_handler_mock(sid="a5198aa4-b3d7-418c-b48f\000793fa2c9bd95"))

        s = SessionManager(session_id="a5198aa4-b3d7-418c-b48f-793fa2c9bd98")
        self.assertIsInstance(s, SessionManager)

    def test_cookie_set(self):
        mock = self.gen_handler_mock()
        sess_manager = SessionManager(mock)
        sid = sess_manager.start_session("some_user_3")
        self.assertIsNotNone(sid)
        call = mock.set_cookie.call_args
        self.assertEqual(call[0][1], sid)
        sess_manager.close_session()


    def test_logout(self):
        sess_manager = SessionManager()
        sid = sess_manager.start_session("some_user_4")
        sess_manager.close_session()
        redis = SessionManager._redis
        self.assertFalse(redis.exists(sess_manager._get_fqn(session_id=sid)))
        self.assertFalse(redis.exists(sess_manager._get_fqn(session_id="some_user_4")))




