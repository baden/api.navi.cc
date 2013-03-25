# -*- coding: utf-8 -*-
__author__ = 'maxaon'
import re


class Filter(object):
    _filters = []

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__

    def filter(self, value):
        for f in self._filters:
            value = f.filter(value)
        return value

    def __call__(self, value):
        return self.filter(value)

    def __add__(self, other):
        if type(self) == type(Filter):
            f = self
        elif type(other) == type(Filter):
            f = other
        else:
            f = Filter()
        f._filters.append(self)
        f._filters.append(other)
        return f


class FilterReplace(Filter):
    def __init__(self, regex, replacement='', count=0, flags=0, name=None):
        super(FilterReplace, self).__init__(name)
        self.regex = regex
        self.replacement = replacement
        self.count = count
        self.flags = flags

    def filter(self, value):
        return re.sub(self.regex, self.replacement, value, self.count, self.flags)


class FilterAlpha(Filter):
    def __init__(self, only_eng=False, allow_whitespaces=False, name=None):
        super(FilterAlpha, self).__init__(name)
        self.only_eng = only_eng
        self.allow_whitespaces = allow_whitespaces
        self.flags = 0

    def filter(self, value):
        whitespaces = "\s" if self.allow_whitespaces else ""
        if self.only_eng:
            regexp = '[^A-Za-z' + whitespaces + ']*'
        else:
            regexp = '[^\w' + whitespaces + ']*'
            self.flags = re.UNICODE

        replace = FilterReplace(regexp, flags=self.flags)
        return replace.filter(value)


class FilterNumbers(Filter):
    def __init__(self, name=None):
        super(FilterNumbers, self).__init__(name)

    def filter(self, value):
        re = '[^0-9]*'
        replace = FilterReplace(re)
        return replace.filter(value)


class Validator(object):
    pass


if __name__ == "__main__":
    fn = FilterNumbers()
    fa = FilterReplace("0")

    print(fn.filter("Some value43"))
    print(fn("4343"))
    print(fa("43ff04"))
    fa2 = FilterReplace("1")

    superfilte = fn + fa + fa2

    print(superfilte.filter("Hello1101199аа"))
