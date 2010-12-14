# -*- coding:utf-8 -*-

import tornado
from tornado.escape import json_encode
from djangornado.conf import settings
from djangornado.utils.importlib import import_module
from djangornado.core.exceptions import ImproperlyConfigured
from djangornado.core.exceptions import NoReturnResponseError

class BaseResponse(object):
    response_data = None

    def return_response(self, handler):
        raise NoReturnResponseError("No response return")

class RenderResponse(BaseResponse):
    def __init__(self, template, context = {}, request_context = None):
        self.response_data = {}
        self.response_data["template"] = template
        self.response_data["context"] = context
        self._load_context()
    
    def _load_context(self):
        if hasattr(settings, "TEMPLATE_CONTEXT_PROCESSORS"):
            for path in settings.TEMPLATE_CONTEXT_PROCESSORS:
                i = path.rfind('.')
                module, attr = path[:i], path[i+1:]
                try:
                    mod = import_module(module)
                except ImportError, e:
                    raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
                try:
                    func = getattr(mod, attr)
                except AttributeError:
                    raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
                self.response_data["context"].update(func())
        return None
    
    def return_response(self, handler):
        if isinstance(self.response_data, dict):
            handler.render(self.response_data.get("template"), **self.response_data.get("context", {}))

class HttpResponse(BaseResponse):
    def __init__(self, response):
        self.response_data = response
    
    def __str__(self):
        if isinstance(self.response_data, unicode):
            self.response_data = self.response_data.encode("utf-8")
        if not isinstance(self.response_data, str):
            self.response_data = str(self.response_data)
        return self.response_data
    
    def __repr__(self):
        return self.response_data
    
    def return_response(self, handler):
        if not isinstance(self.response_data, basestring):
            self.response_data = str(self.response_data)
        handler.write(self.response_data)

class JsonResponse(BaseResponse):
    def __init__(self, response):
        self.response_data = response
    
    def __str__(self):
        return json_encode(self.response_data)
    
    def __repr__(self):
        return self.response_data
    
    def return_response(self, handler):
        handler.set_header("Content-Type", "application/x-javascript")
        handler.write(json_encode(self.response_data))

class HttpResponseRedirect(BaseResponse):
    def __init__(self, url):
        self.url = url

    def return_response(self, handler):
        handler.redirect(self.url)