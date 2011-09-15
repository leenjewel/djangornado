# -*- coding:utf-8 -*-

from djangornado.conf import settings

class DjangornadoRequest(object):
    _attrs = ["POST", "GET", "REQUEST", "session"]
    
    def __init__(self, handler, path, *args, **kwargs):
        self.handler = handler
        self._request_arguments = None
        if path.startswith("/") is False:
            self.path = "/" + path
        else:
            self.path = path
        try:
            self.path = args[0]
        except:
            pass

    def _init_request_arguments(self):
        if (self._request_arguments is None):
            self._request_arguments = {}
            for k in self.handler.request.arguments.keys():
                v = self.handler.get_arguments(k)
                if len(v) == 1:
                    v = v[-1]
                self._request_arguments[k] = v
        return self._request_arguments
    request_arguments = property(_init_request_arguments)
    
    def __getattr__(self, attr):
        if hasattr(self.handler, attr):
            return getattr(self.handler, attr)
        if attr in self._attrs:
            return self
        raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))
    
    def get(self, key, default = None):
        return self.handler.get_argument(key, default)
    
    def items(self):
        return self.request_arguments.items()

    def keys(self):
        return self.handler.request.arguments.keys()

    def values(self):
        return self.handler.request.arguments.values()

    def __getitem__(self, key):
        return self.request_arguments[key]

    def getlist(self, key, strip=True):
        return self.handler.get_arguments(key, strip)

    def get_cookie(self, key):
        if settings.SESSION_COOKIE_SECURE:
            return self.handler.get_secure_cookie(key)
        else:
            return self.handler.get_cookie(key)

    def set_cookie(self, key, value, expires_days=30, **kwargs):
        if settings.SESSION_COOKIE_SECURE:
            self.handler.set_secure_cookie(key, value, expires_days = expires_days, **kwargs)
        else:
            self.handler.set_cookie(key, value, expires_days = expires_days, **kwargs)
