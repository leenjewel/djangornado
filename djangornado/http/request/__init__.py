# -*- coding:utf-8 -*-

class RKRequest(object):
    def __init__(self, handler):
        self.handler = handler
    
    def __getattr__(self, attr):
        if hasattr(self.handler, attr):
            return getattr(self.handler, attr)
        return self
    
    def get(self, key, default = None):
        return self.handler.get_argument(key, default)
