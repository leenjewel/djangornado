# -*- coding:utf-8 -*-

import sys
import traceback
from tornado.web import HTTPError
from tornado.web import RequestHandler
from tornado.web import asynchronous
from djangornado.core.exceptions import NoReturnResponseError
from djangornado.http.request import DjangornadoRequest
from djangornado.http.response import BaseResponse
from djangornado.utils.importlib import import_module
from djangornado.conf import settings, urls
from djangornado.middleware import middleware

class DjangornadoHandler(RequestHandler):

    def _handle_request_exception(self, e):
        if isinstance(e, HTTPError):
            super(DjangornadoHandler, self)._handle_request_exception(e)
        elif settings.has_key("DEBUG") and settings.DEBUG is True:
            exstr = traceback.format_exc()
            self.write("""
                <p><h2>Djangornado Error</h2></p>
                <p>Error Msg:</p><p>%s</p><br>
                <p>Error:</p>
                <div>%s</div>
            """ %(str(e), str(exstr).replace("\n", "<br>")))
            self.finish()
        else:
            print >> sys.stderr, e
            print >> sys.stderr, traceback.format_exc()
            super(DjangornadoHandler, self)._handle_request_exception(HTTPError(500))
    
    def _execute(self, transforms, *args, **kwargs):
        try:
            self._transforms = transforms
            self._dt_request = DjangornadoRequest(self, *args, **kwargs)
            for processer in middleware.request_middleware:
                response = processer(self._dt_request)
                if response and isinstance(response, BaseResponse):
                    self._render_response(response)
                    return self.finish()
            super(DjangornadoHandler, self)._execute(transforms, *args, **kwargs)
        except Exception, e:
            return self._handle_request_exception(e)

    def finish(self, chunk = None):
        for processer in middleware.response_middleware:
            processer(self._dt_request)
        super(DjangornadoHandler, self).finish(chunk)
    
    def get_from_urls(self, pattern):
        asyn = self.get_argument("asyn", False)
        callback, args, kwargs = urls.callback(pattern)
        return callback, args, kwargs, asyn

    def _syn_call(self, callback_func, request, *args, **kwargs):
        self._render_response(callback_func(request, *args, **kwargs))

    @asynchronous
    def _asyn_call(self, callback_func, request, *args, **kwargs):
        result = callback_func(request, *args, **kwargs)
        self._callback(result)
    
    def _callback(self, result):
        self._render_response(result)
        self.finish()
    
    def _render_response(self, response):
        if response is None:
            raise NoReturnResponseError("No response return")
        response.return_response(self)
    
    def get(self, pattern):
        callback, args, kwargs, asyn = self.get_from_urls(pattern)
        if callback is None:
            raise HTTPError(404)
        (self._asyn_call if asyn else self._syn_call)(callback, self._dt_request, *args, **kwargs)

    def post(self, pattern):
        self.get(pattern)