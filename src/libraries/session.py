"""
This module contains SessionMixin, which can be used in RequestHandlers, and
SessionManager, which is the real session manager, and is referenced by the
SessionMixin.

Extracted from "pycket_cookies" but not much
"""
import pickle
from time import time
from uuid import uuid4
import re

from tornado.web import RequestHandler


class SessionError(Exception):
    pass


class SessionManager(object):
    """
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
    """

    SESSION_ID_NAME = 'SESSID'
    EXPIRE_SECONDS = 31 * 24 * 60 * 60
    REDIS_PREFIX = "sess:"
    _redis = None
    session_id = None

    def __init__(self, handler=None, user_id=None, session_id=None):
        """
        Expects a tornado.web.RequestHandler
        @type handler: RequestHandler
        """

        self.handler = handler
        self._user_id = user_id
        self.session_id = self._get_session_id(handler, session_id)
        self.session_started = bool(self.session_id)

        if self.session_started:
            self.expire = self.redis.ttl(self._get_fqn())


    # region Set,Get,Gelete
    def set(self, name, value):
        """
        Sets a value for "name".
        @type value: str|int
        @param name:  Key
        @param value: Value
        """
        if not (isinstance(value, basestring)):
            raise NotImplementedError("Arbitrary data saving not supported yet. Only strings allowed")
        if not self.session_started:
            raise SessionError("Session not started")
            # self.start_session()
        self.redis.hset(self._get_fqn(), name, value)

    def get(self, name, default=None):
        """
        Gets the object for "name", or None if there's no such object. If
        "default" is provided, return it if no object is found.
        """
        if not self.session_started:
            raise SessionError("Session not started")

        return self.redis.hget(self._get_fqn(), name) or default

    def delete(self, *names):
        """
        Deletes the object with "name" from the session, if exists.
        """
        self.redis.hdel(self._get_fqn(), *names)

        # endregion

    # region Session manipulation
    def start_session(self, user_id, restart=False, ):
        """
        Start session for user (defined by `user_id`). Retrieve or generate session id.
        @param restart: Close current session and start new.
        @rtype: str
        @return: Session ID (UUID representation).
        """
        if restart and self.session_id:
            self.close_session()
        if self.session_id is None:
            self.session_id = self._generate_session_id()
            self.expire = self.EXPIRE_SECONDS
            #cleaning user sessions
            self._user_id = user_id or self._user_id
            key_all_user_session = self._get_fqn(session_id=user_id)
            all_user_sessions = self._redis.smembers(key_all_user_session)
            if len(all_user_sessions) != 0:
                pipe = self.redis.pipeline(transaction=False)
                for session in all_user_sessions:
                    pipe.exists(session)
                checked_user_sessions = pipe.execute()
                sessions_to_be_deleted = filter(None, map(lambda mem, res: None if res else mem, all_user_sessions,
                                                          checked_user_sessions))
                if sessions_to_be_deleted:
                    self._redis.srem(key_all_user_session, *sessions_to_be_deleted)

            pipe = self.redis.pipeline()
            pipe.sadd(key_all_user_session, self._get_fqn())
            pipe.hset(self._get_fqn(), "user_id", self._user_id)
            pipe.expire(self._get_fqn(), self.expire)
            pipe.expireat(key_all_user_session, int(self.expire + time() + 1))
            pipe.execute()
            self.session_started = True
            if self.handler:
                self.handler.set_cookie(self.SESSION_ID_NAME, self.session_id, **self.__cookie_settings())
        return self.session_id

    def close_session(self):
        """
        Closes current session and delete all data from db
        """
        pipe = self.redis.pipeline()
        pipe.delete(self._get_fqn())
        pipe.srem(self._get_fqn(session_id=self.user_id), self._get_fqn())
        pipe.execute()
        self.session_id = None
        self.session_started = False

    def close_other_session(self):
        """
        Closes other sessions except current
        """
        keys = set(self.redis.smembers(self._get_fqn(session_id=self.user_id)))
        del_keys = keys.difference([self._get_fqn()])
        if del_keys:
            pipe = self.redis.pipeline()
            pipe.delete(*del_keys)
            pipe.srem(self._get_fqn(session_id=self.user_id), *del_keys)
            pipe.execute()

    # endregion

    @property
    def user_id(self):
        if not self._user_id:
            self._user_id = self.get('user_id')
        return self._user_id

    @property
    def account(self):
        return self._deserialize(self.get('account'))

    @account.setter
    def account(self, value):
        self.set("user_id", str(value['_id']))
        self.set("roles", self._serialize(str(value.get('roles', []))))
        self.set('account', self._serialize(value))

    @account.deleter
    def account(self):
        self.delete('account')

    @property
    def roles(self):
        return self._deserialize(self.get("roles"))

    @property
    def company(self):
        company = self.get('company')
        if not company: #when in guest account return company
            pass
        return company

    @company.setter
    def company(self, value):
        self.set('company', value)

    @company.deleter
    def company(self):
        self.delete('company')

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
    @property
    def redis(self):
        """
        :rtype: redis.Redis
        :return:
        """
        return self._redis

    @redis.setter
    def redis(self, value):
        self._redis = value

    def _serialize(self, value):
        return pickle.dumps(value, pickle.HIGHEST_PROTOCOL)

    def _deserialize(self, value):
        if value is None:
            return None
        return pickle.loads(value)

    def _get_fqn(self, name=None, session_id=None):
        """
        Create fully quantified name from name from prefix, session id and name. If name is empty returns session FQN
        Example:
            name = 'login'
            "sess:a5198aa4-b3d7-418c-b48f-793fa2c9bd95:login"

        @param name: Name to be quantified
        @return: FQN
        """
        name = ":" + name if name else ""
        return self.REDIS_PREFIX + (session_id or self.session_id) + name

    def _get_session_id(self, handler=None, default_session_id=None):
        """
        Return session id from cookie or header and checks it in db
        @return: Session id
        """
        if handler:
            session_id = self.handler.get_cookie(self.SESSION_ID_NAME) \
                or self.handler.request.headers.get("X-API-Nonce")
        else:
            session_id = default_session_id

        if session_id is None:
            return None

        if not isinstance(session_id, basestring) \
            or not re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", session_id.lower()):
            raise SessionError("Wrong format of the session ID")

        if session_id and self.redis.exists(self._get_fqn(session_id=session_id)):
            return session_id
        else:
            return None

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
    """
    This mixin must be included in the request handler inheritance list, so that
    the handler can support sessions.

    Example:
    >>> class MyHandler(tornado.web.RequestHandler, SessionMixin):
    ...    def get(self):
    ...        print type(self.session) # SessionManager

    Refer to SessionManager documentation in order to know which methods are
    available.
    """

    @property
    def session(self):
        """
        Returns a SessionManager instance
        :rtype : SessionManager
        """

        return create_mixin(self, '__session_manager', SessionManager)


def create_mixin(self, manager_property, manager_class):
    if not hasattr(self, manager_property):
        setattr(self, manager_property, manager_class(self))
    return getattr(self, manager_property)


if __name__ == '__main__':
    pass
