# -*- coding: utf-8 -*-
from libraries.web import BaseHandler, BaseRouter, ControllerHandler

__author__ = 'maxaon'

@BaseRouter("/info")
class Info(ControllerHandler):
    __actions__ = ['index']
    i=0
    def get(self):
        self.write("Api server. Called {} times".format(Info.i))
        Info.i+=1

@BaseRouter("/info/about")
class InfoAbout(BaseHandler):
    __actions__ = ['index']
    i=0
    def get(self):
        self.write("Api about. Called {} times".format(Info.i))
        Info.i+=1







