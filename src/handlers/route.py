# -*- coding: utf-8 -*-

from tornado.web import URLSpec


class Route(object):
    """
    The `Route` decorator.
    """

    _routes = []
    """
    Class level list of routes.
    """

    def __init__(self, route, initialize={}, name=None, host=".*$"):
        self.route = route
        self.initialize = initialize
        self.name = name
        self.host = host

    def __call__(self, handler):
        """
        Called when we decorate a class.
        """
        name = self.name or handler.__name__
        spec = URLSpec(self.route, handler, self.initialize, name=name)
        self._routes.append({'host': self.host, 'spec': spec})
        return handler

    @classmethod
    def routes(cls, application=None):
        """
        Method for adding the routes to the `tornado.web.Application`.
        """
        if application:
            for route in cls._routes:
                application.add_handlers(route['host'], route['spec'])
        else:
            return [route['spec'] for route in cls._routes]
