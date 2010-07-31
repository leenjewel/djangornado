# -*- coding:utf-8 -*-

from tornado.web import HTTPError
from tornado.web import RequestHandler
from tornado.web import asynchronous
from djangornado.http.request import DjangornadoRequest
from djangornado.utils.importlib import import_module
from djangornado.conf import settings
from djangornado.http.response import RenderResponse
from djangornado.middleware import middleware

class DjangornadoHandler(RequestHandler):
    def _execute(self, transforms, *args, **kwargs):
        self._rk_request = DjangornadoRequest(self)
        try:
            for processer in middleware.request_middleware:
                processer(self._rk_request)
        except Exception, e:
            self._handle_request_exception(e)
        super(DjangornadoHandler, self)._execute(transforms, *args, **kwargs)
    
    def finish(self, chunk = None):
        try:
            for processer in middleware.response_middleware:
                processer(self._rk_request)
        except Exception, e:
            self._handle_request_exception(e)
        super(DjangornadoHandler, self).finish(chunk)

    def get_from_urls(self, pattern):
        urls = import_module(settings.ROOT_URLCONF)
        callback_func = None
        is_asyn = self._rk_request.get_argument("asyn", False)
        for u in getattr(urls, "urlpatterns", []):
            if u.regex.match(pattern):
                callback_func = u._get_callback()
                return callback_func, is_asyn
        raise HTTPError(404)
    
    def _syn_call(self, callback_func, request):
        self._render_response(callback_func(request))

    @asynchronous
    def _asyn_call(self, callback_func, request):
        result = callback_func(request)
        self._callback(result)
    
    def _callback(self, result):
        self._render_response(result)
        self.finish()
    
    def _render_response(self, response):
        if isinstance(response, RenderResponse):
            self.render(response.template, **response.context)
        self.write(str(response))
    
    def get(self, pattern):
        callback_func, asyn = self.get_from_urls(pattern)
        if callback_func:
            (self._asyn_call if asyn else self._syn_call)(callback_func, self._rk_request)