from copy import deepcopy
import os

import yaml


__author__ = 'maxaon'


class Config(object):
    """
    Represent configuration of the application.

    """
    path = os.path.dirname(__file__)
    __config = None

    @classmethod
    def load(cls, configFile, env=None, personalConfigFile=None, path=None):
        """
        Load configuration for current application
        """
        if not path:
            path = cls.path
        configFile = os.path.abspath(os.path.join(path, configFile))
        config = yaml.load(open(configFile))

        if personalConfigFile:
            personalConfigFile = os.path.abspath(os.path.join(path, personalConfigFile))
            if os.path.isfile(personalConfigFile):
                personalConfig = yaml.load(open(personalConfigFile))
                config = Config.dict_merge(config, personalConfig)
        if env:
            if not env in config:
                raise ValueError("Stage not found in config file")

            if "_extends" in config[env]:
                cls.__config = Config.dict_merge(config[config[env]['_extends']], config[env])
            else:
                cls.__config = config[env]
        else:
            cls.__config = config
        return cls.__config


    @classmethod
    def get(cls, item=None):
        """
        return config item all all config if item=None
        """
        if not item:
            return cls.__config
        return cls.__config[item]

    @staticmethod
    def dict_merge(a, b):
        """recursively merges dict's. not just simple a['key'] = b['key'], if
        both a and bhave a key who's value is a dict then dict_merge is called
        on both values and the result stored in the returned dictionary."""
        if not isinstance(b, dict):
            return b
        result = deepcopy(a)
        for k, v in b.iteritems():
            if k in result and isinstance(result[k], dict):
                result[k] = Config.dict_merge(result[k], v)
            else:
                result[k] = deepcopy(v)
        return result





