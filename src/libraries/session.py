'''
This module contains SessionMixin, which can be used in RequestHandlers, and
SessionManager, which is the real session manager, and is referenced by the
SessionMixin.

Extracted from "pycket_cookies" but not much
'''
from _msi import PID_KEYWORDS
import pickle

from uuid import uuid4
from tornado.web import RequestHandler

class SessionManager(object):
    '''
    This is the real class that manages sessions. All session objects are
    persisted in a Redis database, inside db 0.
    After 1 day without changing a session, it's purged from the dataset,
    to avoid it to grow out-of-control.

    When a session is started, a cookie named 'PYCKET_ID' is set, containing the
    encrypted session id of the user. By default, it's cleaned every time the
    user closes the browser.

    The recommendation is to use the manager instance that comes with the
    SessionMixin (using the "session" property of the handler instance), but it
    can be instantiated ad-hoc.
    '''

    SESSION_ID_NAME = 'SESSID'
    EXPIRE_SECONDS = 31 * 24 * 60 * 60
    PREFIX = ""
    _redis = None
    session_id = None

    def __init__(self, handler):
        '''
        Expects a tornado.web.RequestHandler
        @type handler: RequestHandler
        '''
        self.handler = handler
        self.session_id = self._get_session_id()
        self.session_started = bool(self.session_id)
        if self.session_started:
            self.expire = self._redis.ttl(self._get_fqn(None))

    def set(self, name, value):
        """
        Sets a value for "name".
        @type value: str|int
        @param name:  Key
        @param value: Value
        """
        if not (isinstance(value, basestring) or isinstance(value, int) or isinstance(value, type(None))):
            raise NotImplementedError("Arbitrary data saving not supported yet")
        if not self.session_started: self.start_session()
        name = self._get_fqn(name)
        self._redis.setex(name, value, self.expire)


    def get(self, name, default=None):
        '''
        Gets the object for "name", or None if there's no such object. If
        "default" is provided, return it if no object is found.
        '''
        if not self.session_started: return default
        name = self._get_fqn(name)
        return self._redis.get(name) or default


    def delete(self, names):
        '''
        Deletes the object with "name" from the session, if exists.
        '''
        names = map(self._get_fqn, names)
        self._redis.delete(names)

    def start_session(self, restart=False):
        """
        Start session for user. Retrieve or generate session id.
        @param restart: Close current session and start new.
        @rtype: str
        @return: Session ID (UUID representation).
        """
        if restart and self.session_id:
            self.close_session()
            self.session_id = None
        if self.session_id == None:
            self.session_id = self._generate_session_id()
            self.expire = self.EXPIRE_SECONDS
            self._redis.setex(self._get_fqn(None), self.expire, self.expire)
            if self.handler:
                self.handler.set_cookie(self.SESSION_ID_NAME, self.session_id, **self.__cookie_settings())
        return self.session_id

    def close_session(self):
        """
        Closes current session and delete all data from db
        """
        self.delete(self._get_fqn(None))
        keys = self._redis.keys(self._get_fqn(None) + "*")
        self.delete(keys)

    @property
    def account(self):
        return self.get('account')

    @account.setter
    def account(self, value):
        self.set('account', value)

    @account.deleter
    def account(self):
        self.delete('account')

    #    def __getitem__(self, key):
    #        value = self.get(key)
    #        if value is None:
    #            raise KeyError('%s not found in dataset' % key)
    #        return value
    #
    #    def __setitem__(self, key, value):
    #        self.set(key, value)
    #
    #    def __contains__(self, key):
    #        session = self.__get_session_from_db()
    #        return key in session


    def _get_fqn(self, name):
        """
        Create fully quantified name from name from prefix, session id and name. If name is empty returns session FQN
        Example:
            name = 'login'
            "sess:a5198aa4-b3d7-418c-b48f-793fa2c9bd95:login"

        @param name: Name to be quantified
        @return: FQN
        """
        name = ":" + name if name else ""
        return self.PREFIX + self.session_id + name


    def _get_session_id(self):
        """
        Return session id from cookie or header
        @return: Session id
        """
        session_id = self.handler.get_cookie(self.SESSION_ID_NAME)\
        or self.handler.request.headers.get("X-API-Nonce")
        return session_id

    def _generate_session_id(self):
        """
        Generate session ID. Format is UUID
        @rtype:str
        @return: Session ID
        """
        return str(uuid4())

    def __cookie_settings(self):
        """
        Get setting for cookies
        @rtype: dict
        @return: Cookies settings
        """
        cookie_settings = self.handler.settings.get('cookies', {})
        assert isinstance(cookie_settings, dict)
        #        cookie_settings.setdefault('expires', 3600 * 24 * 7)
        cookie_settings.setdefault('expires_days', 31)
        cookie_settings.setdefault('path', '/')
        cookie_settings.setdefault("HttpOnly", 1)
        return cookie_settings


class SessionMixin(object):
    '''
    This mixin must be included in the request handler inheritance list, so that
    the handler can support sessions.

    Example:
    >>> class MyHandler(tornado.web.RequestHandler, SessionMixin):
    ...    def get(self):
    ...        print type(self.session) # SessionManager

    Refer to SessionManager documentation in order to know which methods are
    available.
    '''

    @property
    def session(self):
        '''
        Returns a SessionManager instance
        '''

        return create_mixin(self, '__session_manager', SessionManager)


def create_mixin(self, manager_property, manager_class):
    if not hasattr(self, manager_property):
        setattr(self, manager_property, manager_class(self))
    return getattr(self, manager_property)

if __name__ == '__main__':
    from database import Redis
    #
    SessionManager._redis = Redis()
    from mock import MagicMock

    handler = MagicMock()

    handler.get_cookie = MagicMock(return_value=None)
    "a5198aa4-b3d7-418c-b48f-793fa2c9bd95"
    handler.request.headers.get = MagicMock(return_value="a5198aa4-b3d7-418c-b48f-793fa2c9bd95")
    s = SessionManager(handler)
    sid = s.start_session()
    print(sid)
    print(s.get("Hello"))
    s.close_session()


