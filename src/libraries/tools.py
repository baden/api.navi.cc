# -*- coding: utf-8 -*-
"""
Module for some tools
"""
import time
import json


class DataConverter(object):
    """
    Converts point information from devices binary information to dictionary and v
    """

    @classmethod
    def to_dict(cls, value):
        value = json.loads(value)

        return value

    @classmethod
    def to_bin(cls, value):
        value = json.dumps(value)
        return value


def i_time():
    """
    time() -> integer number

    Return the current time in seconds since the Epoch.
    No fractions

    :rtype:int
    :return: Current time in seconds since the Epoch.
    """

    return int(time.time())
