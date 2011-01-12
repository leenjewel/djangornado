# -*- coding:utf-8 -*-

from djangornado.conf import settings

class DjangornadoRequest(object):
    _attrs = ["POST", "GET", "REQUEST", "session"]
    
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        try:
            self.path = args[0]
        except:
            pass
    
    def __getattr__(self, attr):
        if hasattr(self.handler, attr):
            return getattr(self.handler, attr)
        if attr in self._attrs:
            return self
        raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))
    
    def get(self, key, default = None):
        return self.handler.get_argument(key, default)
    
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