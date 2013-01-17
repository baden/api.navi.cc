# -*- coding: utf-8 -*-
__author__ = 'maxaon'
import logging
import logging.config
import functools
import inspect

from functools import wraps
from types import FunctionType

class LoggerMixin(object):
    @property
    def logger(self):
        """
        Get logger for current class
        :return: Logger for current class
        :rtype: logging.Logger
        """
        if not hasattr(self, "__logger"):
            logger = logging.getLogger(self.__module__ + self.__class__.__name__)
            setattr(self, '__logger', logger)
        return getattr(self, '__logger')


def log_event(name=None, message_before="Called '{1}' in module {0}",
              message_after="Returned from '{1}' in module {0}",
              verbose=False, level=logging.DEBUG, message_arguments=False, smart=True):
    """
    Decorator to send function log to the event log. Simple calls ``@log_event`` also supported
    :param name: Name of the logger or logger itself.
        If the name is instance of the logger then additional configuration steps added:
        If `logger.level`  isn't enabled for level, then decorator will not be applied. To omit this behavior set `smart` to ``False``
        Default name is '<module>.<class_name>'
    :param message_before: Message before calling the method. If `message_before` == ``None`` no log message will be shown
                Format params:
                0     - module name
                1     - function name (with class name)
                named - function parameters if `message_arguments`=``True``
                Default: "Called '{1}' in module {0}"
    :param message_after :Message after calling the method. If `message_after` == ``None`` no log message will be shown
                0     - module name
                1     - function name (with class name)
                2     - returned value
                named - function parameters if message_arguments=true
                Default:"Returned from '{1}' in module {0}"
    :param verbose: If verbose is true function params and return value will be logged. Default: ``False``
    :param level: Log-level for the log. Default to ``False``
    :param message_arguments: If ``True`` function arguments will be passed to format function as a dict. Default: ``False``
    :return:
    """

    def wrapper(f):
        # if name was supplied test for current logger level
        if name and smart:
            logger = name if isinstance(name, logging.getLoggerClass()) else logging.getLogger(name)
            if not logger.isEnabledFor(level):
                return f
                # Determines tes whether ``f`` is method or function
        is_method = inspect.getargspec(f)[0][0] == 'self'
        is_class_method = inspect.getargspec(f)[0][0] == 'cls'

        @wraps(f)
        def decorator(*args, **kwargs):
            #get caller class
            self = args[0] if is_method else None
            cls = args[0] if is_class_method else None
            #define class name and logger name
            class_name = self.__class__.__name__ if is_method else cls.__name__ if is_class_method else ''
            if name:
                logger_name = name
            elif is_method or is_class_method:
                logger_name = f.__module__ + "." + class_name
            else:
                logger_name = f.__module__
            logger = logging.getLogger(logger_name) if isinstance(logger_name, str) else logger_name
            #test for logger level
            if not logger.isEnabledFor(level):
                return f(*args, **kwargs)

            function_name = class_name + "." + f.__name__ if is_method or is_class_method else f.__name__
            function_module = f.__module__
            #get function arguments in dictionary. Slow operation
            call_args = inspect.getcallargs(f, *args, **kwargs) if message_arguments else {}
            #            call_args={}
            #Easy calling of log function
            log = functools.partial(logger.log, level)
            if message_before:  log(message_before.format(function_module, function_name, **call_args))
            if verbose:
                log("Arguments:")
                for arg_name in call_args:
                    log("\t{0} : {1}".format(arg_name, call_args[arg_name]))
            return_value = f(*args, **kwargs)
            if message_after:   log(message_after.format(function_module, function_name, return_value, **call_args))
            if verbose:         log("\t returned: {}".format(return_value))
            return return_value

        return decorator

    # Fix when decorator called whiteout brackets
    if type(name) is FunctionType:
        f = name
        name = None
        return wrapper(f)
    return wrapper

# some simple tests
class _NotDecorated(object):
    def function(self, params):
        return params * 4


class _Decorated(object):
    @log_event
    def function(self, params):
        return params * 4


class _DecoratedWhitLogger(object):
    logger = logging.getLogger(__name__ + ".DecoratedWhitLogger")
    logger.setLevel(logging.DEBUG)

    @log_event(logger)
    def function(self, params):
        return params * 4

itercount = 10 ** 4

def _testNotDecorated():
    d = _NotDecorated()
    for i in xrange(itercount):
        d.function(i)


def _testDecorated():
    d = _Decorated()
    for i in xrange(itercount):
        d.function(i)


def _testDecoratedPlus():
    d = _DecoratedWhitLogger()
    for i in xrange(itercount):
        d.function(i)


def profile():
    d = _Decorated()
    d.function(4)

    import profile as p

    print("Not decorated")
    p.run("_testNotDecorated()")
    print("Decorated with logger")
    p.run("_testDecoratedPlus()")
    print("Decorated")
    p.run("_testDecorated()")


if __name__ == "__main__":
    logging.config.dictConfig({
        'loggers': {
            'libraries': {'level': 'DEBUG'},
            '__main__.DecoratedWhitLogger': {'level': 'DEBUG'},
            'TestClass': {'level': 'DEBUG'},
            "aaa": {'level': 'DEBUG'}
        },
        'version': 1,
        'root': {
            'handlers': ['null'],
            'level': 'DEBUG'
        },
        'handlers': {
            'null': {
                'formatter': 'default',
                'class': 'logging.NullHandler',
            },
            'console': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stderr'}
        },
        'formatters': {
            'default': {
                'format': '%(message)s'}
        }
    })
    profile()
