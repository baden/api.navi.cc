# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, with_statement
from json import loads, dumps
import calendar
import email.utils
import time

import tornado.testing
from tornado.httpclient import HTTPResponse, HTTPRequest
from tornado.escape import utf8
from tornado import httputil

from configs import Config
import application.controllers


__author__ = 'maxaon'

config = Config.load("application.yaml", "testing", "application-personal.yaml")

GET = "GET"
POST = "POST"
PATCH = "PATCH"
DELETE = "DELETE"


class AsyncHTTPTestCase(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        app = application.Application('testing', config)
        app.bootstrap()
        return app


    def get_http_port(self):
        return super(AsyncHTTPTestCase, self).get_http_port() + 1024

    def fetch(self, path, **kwargs):
        """\
        Convenience method to synchronously fetch a url.

        The given path will be appended to the local server's host and port.
        Any additional kwargs will be passed directly to
        AsyncHTTPClient.fetch (and so could be used to pass method="POST",
        body="...", etc).

        :param path: URL path
        :param kwargs:
        :rtype: tornado.httpclient.HTTPResponse
        :return:
        """
        self.response = super(AsyncHTTPTestCase, self).fetch(path, **kwargs)

        assert isinstance(self.response, HTTPResponse)
        return self.response

    def assertResponseCode(self, code):
        self.assertEqual(self.response.code, code)

    inter = u"Iñtërnâtiônàlizætiøn Iñtërnâtiônàlizætiøn"


class JsonHTTPRequest(HTTPRequest):
    """HTTP client request object."""

    def __init__(self, url, method="GET", headers=None,
                 auth_username=None, auth_password=None,
                 connect_timeout=20.0, request_timeout=20.0,
                 if_modified_since=None, follow_redirects=True,
                 max_redirects=5, user_agent=None, use_gzip=True,
                 network_interface=None, streaming_callback=None,
                 header_callback=None, prepare_curl_callback=None,
                 proxy_host=None, proxy_port=None, proxy_username=None,
                 proxy_password='', allow_nonstandard_methods=False,
                 validate_cert=True, ca_certs=None,
                 allow_ipv6=None,
                 client_key=None, client_cert=None):
        """Creates an `HTTPRequest`.

        All parameters except `url` are optional.

        :arg string url: URL to fetch
        :arg string method: HTTP method, e.g. "GET" or "POST"
        :arg headers: Additional HTTP headers to pass on the request
        :type headers: `~tornado.httputil.HTTPHeaders` or `dict`
        :arg string auth_username: Username for HTTP "Basic" authentication
        :arg string auth_password: Password for HTTP "Basic" authentication
        :arg float connect_timeout: Timeout for initial connection in seconds
        :arg float request_timeout: Timeout for entire request in seconds
        :arg datetime if_modified_since: Timestamp for ``If-Modified-Since``
           header
        :arg bool follow_redirects: Should redirects be followed automatically
           or return the 3xx response?
        :arg int max_redirects: Limit for `follow_redirects`
        :arg string user_agent: String to send as ``User-Agent`` header
        :arg bool use_gzip: Request gzip encoding from the server
        :arg string network_interface: Network interface to use for request
        :arg callable streaming_callback: If set, `streaming_callback` will
           be run with each chunk of data as it is received, and
           `~HTTPResponse.body` and `~HTTPResponse.buffer` will be empty in
           the final response.
        :arg callable header_callback: If set, `header_callback` will
           be run with each header line as it is received, and
           `~HTTPResponse.headers` will be empty in the final response.
        :arg callable prepare_curl_callback: If set, will be called with
           a `pycurl.Curl` object to allow the application to make additional
           `setopt` calls.
        :arg string proxy_host: HTTP proxy hostname.  To use proxies,
           `proxy_host` and `proxy_port` must be set; `proxy_username` and
           `proxy_pass` are optional.  Proxies are currently only support
           with `curl_httpclient`.
        :arg int proxy_port: HTTP proxy port
        :arg string proxy_username: HTTP proxy username
        :arg string proxy_password: HTTP proxy password
        :arg bool allow_nonstandard_methods: Allow unknown values for `method`
           argument?
        :arg bool validate_cert: For HTTPS requests, validate the server's
           certificate?
        :arg string ca_certs: filename of CA certificates in PEM format,
           or None to use defaults.  Note that in `curl_httpclient`, if
           any request uses a custom `ca_certs` file, they all must (they
           don't have to all use the same `ca_certs`, but it's not possible
           to mix requests with ca_certs and requests that use the defaults.
        :arg bool allow_ipv6: Use IPv6 when available?  Default is false in
           `simple_httpclient` and true in `curl_httpclient`
        :arg string client_key: Filename for client SSL key, if any
        :arg string client_cert: Filename for client SSL certificate, if any
        """
        if headers is None:
            headers = httputil.HTTPHeaders()
        headers.add('Content-Type', 'application/json; charset=utf-8')
        if if_modified_since:
            timestamp = calendar.timegm(if_modified_since.utctimetuple())
            headers["If-Modified-Since"] = email.utils.formatdate(
                timestamp, localtime=False, usegmt=True)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self._url = url
        self.method = method
        self.headers = headers

        self.auth_username = auth_username
        self.auth_password = auth_password
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.user_agent = user_agent
        self.use_gzip = use_gzip
        self.network_interface = network_interface
        self.streaming_callback = streaming_callback
        self.header_callback = header_callback
        self.prepare_curl_callback = prepare_curl_callback
        self.allow_nonstandard_methods = allow_nonstandard_methods
        self.validate_cert = validate_cert
        self.ca_certs = ca_certs
        self.allow_ipv6 = allow_ipv6
        self.client_key = client_key
        self.client_cert = client_cert
        self.start_time = time.time()

    _body = {}
    params = {}
    _url = ""
    _parameters = ""

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def rb(self):

        """

        :rtype:dict
        :return:
        """
        return self._body

    @rb.setter
    def rb(self, value):
        self._body = value


    @property
    def url(self):
        return utf8(dumps(self._body))

    @url.setter
    def url(self, value):
        raise NotImplementedError

    @property
    def body(self):
        return utf8(dumps(self._body))

    @body.setter
    def body(self, value):
        if isinstance(value, dict):
            self._body = value
        elif isinstance(value, basestring):
            try:
                self._body = loads(value)
            except:
                raise AttributeError("Unable to parse json")
        else:
            raise AttributeError("Body must be dict or json")











