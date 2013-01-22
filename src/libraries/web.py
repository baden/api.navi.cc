# -*- coding: utf-8 -*-
from copy import deepcopy
import logging
from tornado.httpserver import HTTPRequest

from tornado.web import RequestHandler, HTTPError, URLSpec
import tornado.web
from types import FunctionType
from application import BaseCollection
from libraries.logger import log_event
from libraries.session import SessionManager

__author__ = 'maxaon'

#region Status codes
# status codes
# informational
CONTINUE = 100
SWITCHING_PROTOCOLS = 101

# successful
OK = 200
CREATED = 201
ACCEPTED = 202
NON_AUTHORITATIVE_INFORMATION = 203
NO_CONTENT = 204
RESET_CONTENT = 205
PARTIAL_CONTENT = 206
MULTI_STATUS = 207
IM_USED = 226

# redirection
MULTIPLE_CHOICES = 300
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
NOT_MODIFIED = 304
USE_PROXY = 305
TEMPORARY_REDIRECT = 307

# client error
BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
REQUEST_ENTITY_TOO_LARGE = 413
REQUEST_URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
REQUESTED_RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417
UNPROCESSABLE_ENTITY = 422
LOCKED = 423
FAILED_DEPENDENCY = 424
UPGRADE_REQUIRED = 426

# server error
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
INSUFFICIENT_STORAGE = 507
NOT_EXTENDED = 510

# Mapping status codes to official W3C names
responses = {
    100: 'Continue',
    101: 'Switching Protocols',

    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',

    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)',
    307: 'Temporary Redirect',

    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',

    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
}
#endregion

FILTER_INCLUDE = 1
FILTER_EXCLUDE = 0

class RemoveItem(object):
    '''
    Empty class for filter functionality. When it rise element is skipped. For filter only
    '''
    pass


class BaseHandler(RequestHandler):
    '''
    Base handler for using in application
    '''

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    @property
    def session(self):
        """
        Return session manager for session working
        :returns: Session manager
        :rtype: libraries.session.SessionManager
        """
        if not hasattr(self, "__session_manager"):
            setattr(self, "__session_manager", SessionManager(self))
        return getattr(self, "__session_manager")


class ControllerHandler(BaseHandler):
    '''\
    Handler for pretty request like /route_regex/:action
    Not implemented fully as I desire
    '''
    #: :list: List of string of available action
    __actions__ = None

    def __init__(self, application, request, **kwargs):
        super(ControllerHandler, self).__init__(application, request, **kwargs)
        self.__actions__ = []

    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms.
        Npt completed!!!
        """
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
                # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in ("GET", "HEAD", "OPTIONS") and\
               self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()
            self.prepare()
            if not self._finished:
                args = [self.decode_argument(arg) for arg in args]
                kwargs = dict((k, self.decode_argument(v, name=k))
                    for (k, v) in kwargs.iteritems())
                getattr(self, self.request.method.lower())(*args, **kwargs)
                if self._auto_finish and not self._finished:
                    self.finish()
        except Exception as e:
            self._handle_request_exception(e)


class RestHandler(BaseHandler):
    '''
    Handler for REST request.
    Process of execution:

    __init__() -> _execute() -> xsrf() if enabled -> prepare() -> _get_id_and_action() -> data filtering:
        calling method `filter_<action>()` or filtering using `simple filters` if `action` in this dict
    -> args and (request params + kwargs) encoding -> <action>(*args, **kwargs) -> filter_response() -> write_object()
    ======
    Filtering
    ======
    Class provides simple filtering method. Dictionary `simple_filters` has keys  which are method names(like 'get','post') and value is filtering actions.

    Example of dictionary:
        simple_filters = {
        "get": {...},
        "post": {...},
        "put": {...},
        "delete": {...},
        "some_action": {...},
      }

    Modes:
        - Exclusion: provided keys will be deleted. All values MUST be equivalent to '0' (for now)
        - Inclusion: only provided keys will be filtered. All values MUST be equivalent to '1'
    Format of the dictionary values:
        0 - exclude key
        1 - include key
        2 - include key, and this key is required
        also function can be provided. It will be called with parameters: (key,value).
            As a return value `Exception` can be returned. It will be raised.
            If spatial object `libraries.web.RemoveItem` returned this value will be excluded from the filter result.
    Examples:
        Inclusion mode:
            {'field_name': 1, 'other_field_name': 1,
                 'simple_filter_using_lambda_or_otherFunction': lambda key, value: value if value and value <30 else None,
                 'exclude value': lambda key, value: value if value and value >30 else RemoveItem(),
                 'filter_and_error': lambda key, value: value if value and value in ('a','b') else RestError('filter_and_error must be 'a' or 'b')}
        Exclusion mode:
            {'undesired_key': 0, 'secret_phrase': 0'}

    ======
    Function arguments
    ======
    If route has key 'id' first parameter is model, founded by this id by function get_model()
    If request params where filtered (using simple filters or by calling filter_<action>()) the second(or first if no id) param is filtered data
    '''

    simple_filters = {}
    defaults = {
        "get": {},
        "post": {},
        "put": {},
        "delete": {}
    }
    _actions_ = []
    _object_actions_ = []
    _collection = None
    primary = None

    def __init__(self, application, request, **kwargs):
        super(RestHandler, self).__init__(application, request, **kwargs)
        self.add_rest_headers()


    @property
    def collection(self):
        """
        Return collection for this RestHandler
        :return: Collection
        :rtype: BaseCollection
        """
        if not isinstance(self._collection, BaseCollection):
            if isinstance(self._collection, str):
                self._collection = self.application.db.collection(self._collection)
            elif issubclass(self._collection, BaseCollection): ## TODO wtf. Почему type(self._collection) == type(type)
                self._collection = self._collection()
        return self._collection


    #region Filters
    def determinate_mode(self, filter_settings):
        mode = None
        for action in filter_settings.values():
            if type(action) == FunctionType:
                continue
            if (action == FILTER_INCLUDE or action == FILTER_EXCLUDE):
                if mode == None:
                    mode = action
                    continue
                if action != mode:
                    raise ValueError("Multiple modes detected")
        if mode == None: mode = FILTER_INCLUDE
        return mode

    def filter_params(self, params, filter_settings):
        '''
        Filter data in 'params' using filter_settings
        Format of the filter settings dictionary:
        See class desription
        If filterSetting is empty no filtering provided
        '''
        if not filter_settings:
            return params
        mode = self.determinate_mode(filter_settings)

        filtered_values = {} if mode == FILTER_INCLUDE else deepcopy(params)

        for key, action in filter_settings.iteritems():
            if type(action) == FunctionType:
                try:
                    result = action(key, params.get(key))
                    if isinstance(result, Exception):
                        raise result
                    filtered_values[key] = result
                except RemoveItem:
                    del filtered_values[key]
            elif key not in params:
                if action == 2:
                    raise RestError("Required field {} is empty".format(key))
                continue
            elif mode == FILTER_INCLUDE:
                filtered_values[key] = params[key]
            elif mode == FILTER_EXCLUDE:
                del filtered_values[key]

        return filtered_values

    #endregion

    def get_model(self, id):
        '''
        Retrieve model from the `collection` by `id` using self._primary information
        :param id: Primary key
        :return:
        '''
        if self.collection:
            return self.collection.find_by_primary(id)
        return None

    request = HTTPRequest

    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
                # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in ("GET", "HEAD", "OPTIONS") and\
               self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()
            self.prepare()
            if not self._finished:
                id, action = self._get_id_and_action(*args, **kwargs)

                if hasattr(self, 'filter_' + action):
                    filtered_data = getattr(self, 'filter_' + action)(self.params())
                elif self.simple_filters.has_key(action):
                    filtered_data = self.filter_params(self._get_params(), self.simple_filters[action])
                else:
                    filtered_data = {}

                args = [self.decode_argument(arg) for arg in args]
                kwargs = dict(self.params(), **kwargs)
                kwargs = dict((k, self.decode_argument(v, name=k))
                    for (k, v) in kwargs.iteritems())

                kwargs['data'] = filtered_data
                if id:
                    kwargs['id'] = id
                result = getattr(self, action)(*args, **kwargs)
                if result != None:
                    result = self.filter_response(result, id=id, action=action)
                    self.write_object(result)

                if self._auto_finish and not self._finished:
                    self.finish()
        except RestError as e:
            self.send_error(e.status_code, ex=e)
        except Exception as e:
            self._handle_request_exception(e)

    def _get_id_and_action(self, *args, **kwargs):
        '''
        Convert request parameters to the id and action
        :param args: Positional variables from the router
        :param kwargs: KW variables from the router
        :return: Return tuple of id and action
        :rtype: (id,action)
        '''
        id = kwargs.get('id')
        if id and id in self._actions_: return None, id

        object_action = kwargs.get('action')
        if object_action and object_action.lower() in self._object_actions_: return id, object_action.lower()

        request_method = self.request.method.lower()
        if not id and request_method == 'get': return None, 'index'
        if not id and request_method == 'post': return None, 'post'

        return id, request_method

    #region Rest methods

    def index(self, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def get(self, id, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def head(self, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def post(self, data, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def delete(self, id, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def patch(self, id, data, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def put(self, id, data, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)

    def options(self, *args, **kwargs):
        raise RestError(NOT_IMPLEMENTED)
        #endregion


    def write_error(self, status_code, **kwargs):
        err_msg = {"error": {"status": status_code}}
        if 'ex' in kwargs:
            if hasattr(kwargs['ex'], 'message'):
                err_msg['error']['message'] = kwargs['ex'].message
        self.write_object(err_msg)

    def params(self):
        '''
        Return decoded params from the request in normal style (key:value) in dictionary
        :return: All params
        '''
        return self._get_params()

    def param(self, name, default=None):
        '''
        Return parameter identified by `name` from request
        :param name: Name of parameter
        :param default: Default value for parameter
        :return:
        '''
        return self._get_params().get(name, default)

    def _get_params(self):
        '''
        Converts parameter from request to normal representation and decode them.
        :return:
        '''
        data = self.request.arguments
        result = {}
        for d in data:
            position = len(data[d]) - 1
            result[str(d)] = self.decode_argument(data[d][position], name=d)if position >= 0 else None
        return result

    def add_rest_headers(self):
        '''
        Adds headers to response according to the request(Not Implemented)
        '''
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json; charset=utf-8')

    def write_object(self, result):
        '''
        Write serialized response object
        :type result: dict, RestResponse
        :param result:

        '''
        if isinstance(result, RestResponse):
            self.set_status(result.code)
            data = result.data
        else:
            data = result
        from bson.json_util import dumps

        self.write(dumps(data))

    def filter_response(self, response, **kwargs):
        '''
        Filter response object. If response has method 'filter_response' it will be used. In another case simple filters will be used
        :param response: Response object
        :param kwargs:
        :return: Filtered response
        '''
        if hasattr(response, 'filter_response'):
            return getattr(response, 'filter_response')(response)
        elif isinstance(response, RestResponse):
            response.data = self.filter_params(response.data, self.simple_filters.get("response", {}))
            return response
        return self.filter_params(response, self.simple_filters.get("response", {}))


class RestResponse(object):
    '''
    Container for keeping response code and data in one place
    '''

    def __init__(self, code=200, data=None):
        self.code = code
        self.data = data


class RestError(HTTPError):
    '''
    Exception to be shownt ot the user
    '''

    def __init__(self, status_code=400, message=None, internal_code=0):
        """
        :param status_code: Code if response. Default is 400. If status code is ``str`` it will be treated as message
        :param message: Message for the error. Default: according to status code
        :param internal_code: Internal error code. Default is '0'
        """
        if isinstance(status_code, basestring):
            message = status_code
            status_code = 400
        self.status_code = status_code
        self.message = message if message else responses[self.status_code]
        self.internal_code = internal_code


class BaseRouter(object):
    '''
    Base representation of router
    Base Path will be appended to each route (Not implemented)
    '''
    _routes = []
    basepath = None


    def __init__(self, route, initialize=None, name=None, host=".*$", add_basepath=True):
        self.route = route
        self.initialize = initialize if initialize else {}
        self.name = name
        self.host = host
        self.add_basepath = add_basepath

    def __call__(self, handler):
        """
        Called when we decorate a class.
        """
        name = self.name or handler.__name__
        spec = URLSpec(self.route, handler, self.initialize, name=name)
        self._routes.append({'host': self.host, 'spec': spec})
        return handler


    @classmethod
    def getAllRoutes(cls):
        return [route['spec'] for route in cls._routes]


class RestRoute(BaseRouter):
    '''
    Routing for rest request
    '''

    def __init__(self, route=None, initialize=None, name=None, host=".*$", add_basepath=True, defaults=None):
        """
        Initialize router.
        Router can contain regex strings::
            "{{id}}" will be replaced to id regex
            "{{action"" well be replaced to action regex
            Warning: don't insert slashes('/')!
        :type add_basepath: bool
        :type route: str
        :param route: Regexp string for router. Can contain '{{id}}' and '{{action}}'. Don't add slashes!
        :param initialize: Initialize params for the handler class
        :param name: Name of the router
        :param host: Host to the router
        :param add_basepath: If ``False`` will not prepend basepath
        :param defaults: Default values for the router
        """
        super(RestRoute, self).__init__(route, initialize, name, host, add_basepath=add_basepath)
        self.defaults = defaults

        # TODO add lookbehind condition to slashes

    REGEX_ID = r'(?:/)*(?P<id>[^/]+)?(?:/)*'
    REGEX_ACTION = "(?:/)*(?P<action>{0})?(?:/)*"

    def __call__(self, handler):
        """
        Called when we decorate a class.
        """
        name = self.name or handler.__name__
        route = self.route or "/" + name.lower() + "{{id}}{{action}}"
        if "{{id}}" in route: route = route.replace("{{id}}", self.REGEX_ID)
        if handler._object_actions_:
            action_regexp = self.REGEX_ACTION.format("|".join(handler._object_actions_))
            if "{{action}}" in route:
                route = route.replace("{{action}}", action_regexp)
            else:
                route += action_regexp
        else:
            route = route.replace("{{action}}", "")

        handler._default_router_params = self.defaults
        spec = URLSpec(route, handler, self.initialize, name=name)
        BaseRouter._routes.append({'host': self.host, 'spec': spec})

        return handler

#    @staticmethod
#    def route(handler, request, args, kwargs):
#        path = kwargs['__other__'].split("/")
#        del path[0]
#        id = None
#        request_method = request.method.lower()
#
#        if len(path) == 0:
#            action = 'index' if request_method == "get" else 'post'
#        elif request_method in ['put', 'delete', 'patch']:
#            id = path[0]
#            action = request.method.lower()
#        elif request_method == 'post'and len(path) == 2 and path[1] in getattr(handler, "__object_actions__", {}):
#            #actions under the object /account/3423423/email
#            id = path[0]
#            action = re.sub("[^a-z0-9_]", "", path[1].lower())
#            #        if len(path) != 0:
#            #            for i in range(0, len(path), 2):
#            #                kwargs[path[i]] = path[i + 1] if len(path) < i + 1 else None
#            #        del kwargs['__other__']
#        elif request_method in ('post', 'get') and path[0] in getattr(handler, "_actions_", {}):
#            action = path[0]
#        else:
#            raise RestError("Unable to determinate action")
#        return (action, id, kwargs)


class Application(tornado.web.Application):
    '''
    Rest application
    '''
    logger = logging.getLogger(__name__ + ".Application")
    environment = "production"

    def __init__(self, environment, settings, handlers=None):
        self.environment = environment or "production"
        self.settings = settings

        if not handlers: handlers = []
        if 'handlers' in settings:
            handlers.extend(settings.pop('handlers'))
        handlers.extend(BaseRouter.getAllRoutes())
        super(Application, self).__init__(handlers, **self.settings)

    def bootstrap(self):
        '''
        Initialize application(tornado.web.Application)
        :return:
        '''

        for host, handlers in self.handlers:
            for handler in handlers:
                if handler._path:
                    self.logger.debug("http://localhost" + handler._path)
                else:
                    self.logger.debug("pattern: " + handler.regex.pattern)


    @log_event(logger, message_before="Running application")
    def run(self, **kwargs):
        '''
        Run server: start listening and start IOLoop
        :param kwargs: Sended to HTTPServer
        :return:
        '''
        from tornado.httpserver import HTTPServer

        server = HTTPServer(self, **kwargs)
        port = self.settings.get('port', 8080)
        address = self.settings.get('address', 'localhost')
        server.listen(port, address=address)
        self.logger.info("Application listening at http://{address}:{port}".format(port=port, address=address))

        #TODO Maybe move from here to main app
        from tornado.ioloop import IOLoop

        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            IOLoop.instance().stop()

    def listen(self, port, address="", **kwargs):
        """Starts an HTTP server for this application on the given port.

        This is a convenience alias for creating an HTTPServer object
        and calling its listen method.  Keyword arguments not
        supported by HTTPServer.listen are passed to the HTTPServer
        constructor.  For advanced uses (e.g. preforking), do not use
        this method; create an HTTPServer and call its bind/start
        methods directly.

        Note that after calling this method you still need to call
        IOLoop.instance().start() to start the server.
        """
        # import is here rather than top level because HTTPServer
        # is not importable on appengine
        from tornado.httpserver import HTTPServer

        server = HTTPServer(self, **kwargs)
        server.listen(port, address)


    def __call__(self, request):
        """Called by HTTPServer to execute the request. Trims slashes"""
        request.path = request.path.rstrip("/")
        return super(Application, self).__call__(request)


if __name__ == "__main__":
    pass
