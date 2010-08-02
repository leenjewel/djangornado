# -*- coding:utf-8 -*-

class DjangornadoRequest(object):
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        try:
            self.path = args[0]
        except:
            pass
    
    def __getattribute__(self, attr):
        if hasattr(self.handler, attr):
            return getattr(self.handler, attr)
        elif hasattr(self, attr):
            return getattr(self, attr)
        return self
    
    def get(self, key, default = None):
        return self.handler.get_argument(key, default)
