# -*- coding:utf-8 -*-

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
