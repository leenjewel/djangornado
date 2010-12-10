# -*- coding:utf-8 -*-
'''
Created on 2010-12-3

@author: leenjewel
'''

import os, re, code
from djangornado.core.management.base import NoArgsCommand
from djangornado.middleware import middleware
from djangornado.conf import urlpatterns
from optparse import make_option

class UnitTestRequest(object):
    
    def __init__(self, unittest_options):
        self.cookie_params = {}
        self.runmiddleware = unittest_options.get("runmiddleware", False)

    @staticmethod
    def make(url):
        if (url.startswith("http://") or url.startswith("https://")) is False:
            url = "http://" + url
        urllist = url.split("?")
        url = urllist[0]
        urlparams = {}
        if len(urllist) == 2:
            for key, value in [kv.split("=") for kv in urllist[1].split("&")]:
                if urlparams.has_key(key):
                    urlparams[key] = [urlparams[key]]
                    urlparams[key].append(value)
                urlparams[key] = value
        return url, urlparams
    
    def __getattr__(self, attr):
        if attr in ("POST", "REQUEST", "GET"):
            return self.urlparams
        elif attr in ("_cookies",):
            return self
        raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))
    
    def get_cookie(self, cookie_name):
        return self.cookie_params.get(cookie_name) or self.urlparams.get(cookie_name)
    
    def get_secure_cookie(self, cookie_name):
        return self.get_cookie(cookie_name)
    
    def set_cookie(self, cookie_name, cookie_value, *args, **kwargs):
        self.cookie_params[cookie_name] = cookie_value
        return
    
    def set_secure_cookie(self, cookie_name, cookie_value, *args, **kwargs):
        self.set_cookie(cookie_name, cookie_value, *args, **kwargs)
    
    def get(self, key, default_value = None):
        return self.cookie_params.get(key, default_value) or self.urlparams.get(key, default_value)
    
    def getlist(self, key):
        return_list = self.urlparams.get(key)
        if isinstance(return_list, (list, tuple)):
            return return_list
        return []
    
    def get_url_path(self):
        urllist = self.url.split("/")
        urlpath = ""
        urlindex = len(urllist)-1
        while urlindex > 0:
            if "." in urllist[urlindex]:
                break
            if urllist[urlindex]:
                urlpath = urllist[urlindex] + "/" + urlpath
            urlindex -= 1
        if self.url[-1] != "/":
            urlpath = urlpath[:-1]
        return urlpath
    
    def run_url(self, url):
        self.url, self.urlparams = self.make(url)
        self.urlpath = self.get_url_path()
        if self.runmiddleware:
            self.run_middleware()
        callback_func = urlpatterns.callback(self.urlpath)
        if callback_func is None:
            return "HTTP(404)"
        url_result = callback_func(self)
        if self.runmiddleware:
            self.run_middleware(isrequest = False)
        return url_result
    
    def run_middleware(self, isrequest = True):
        if isrequest:
            unit_middleware = middleware.request_middleware
        else:
            unit_middleware = middleware.response_middleware
        for processer in unit_middleware:
            response = processer(self)
            if response and isrequest:
                return response
        return
    
    def print_log(self, loglist, kmax = 0, vmax = 0, logstr = ""):
        for k, v in loglist:
            if len(k) > kmax:
                kmax = len(k)
            if isinstance(v, basestring) and len(v) > vmax:
                vmax = len(v)
        for k, v in loglist:
            ks = (kmax-len(k)+1)
            vs = (vmax-len(v)+1)
            logstr += "| "+k+" "*ks+"| "+v+" "*vs+"|\n+"+"-"*(kmax+vmax+5)+"+\n"
        logstr = "+"+"-"*(kmax+vmax+5)+"+\n"+logstr
        return logstr
        
    
    def http(self, url):
        url_result = self.run_url(url)
        urllog = []
        urllog.append(["URL", self.url])
        urllog.append(["PATH", self.urlpath])
        urllog += self.urlparams.items()
        print self.print_log(urllog)
        print url_result
        return

class Command(NoArgsCommand):
    
    option_list = NoArgsCommand.option_list + (
        make_option('--runmiddleware', action='store_true', dest='runmiddleware',
            help='Tells Djangornado to start a unit test with middleware.'),
    )
    help = "Runs a Python interactive interpreter to test your application."
    
    requires_model_validation = False
    
    UNITTEST_OPTIONS = {
        "runmiddleware":False,
    }
    
    def handle(self, *args, **kwargs):
        unittest_options = self.UNITTEST_OPTIONS.copy()
        unittest_options.update(kwargs)
        for op in args:
            if "=" in op:
                k,v = op.split("=")
            else:
                k,v = op, True
            unittest_options[k.lower()] = v
        unittest_request = UnitTestRequest(unittest_options)
        code.interact("=*= Djangornado Unit Test =*=", local = {"request":unittest_request})