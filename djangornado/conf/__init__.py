# -*-coding:utf-8 -*-

import os
import re
from djangornado.utils.importlib import import_module
from djangornado.core.urlresolvers import RegexURLPattern, RegexURLResolver

__all__ = ['settings', 'urls']

ENVIRONMENT_VARIABLE = 'DJANGORNADO_SETTINGS_MODULE'

class LazySettings(dict):
    def __init__(self):
        try:
            settings_path = os.environ[ENVIRONMENT_VARIABLE]
            if not settings_path:
                raise KeyError
        except KeyError:
            raise ImportError('No settings file path given, because environment variable %s is undefined.' % ENVIRONMENT_VARIABLE)
        self.settings_module = import_module(settings_path)
        self.settings_dict = self.settings_module.__dict__
        super(LazySettings, self).__init__(self.settings_dict.items())
        self.initialize()
    
    def initialize(self):
        self["debug"] = False
        if self.has_key("DEBUG"):
            self["debug"] = self["DEBUG"]
        if self.has_key("TEMPLATE_DIRS"):
            self["template_path"] = self["TEMPLATE_DIRS"]
    
    def __getattr__(self, attr):
        if self.has_key(attr):
            return self.get(attr)
        raise AttributeError("%s instance has no attribute '%s'" %(self.__class__.__name__, attr))

settings = LazySettings()

class LazyUrls(object):
    def __init__(self):
        if not hasattr(settings, "ROOT_URLCONF"):
            raise ImportError('No settings.ROOT_URLCONF given.')
        urls = import_module(settings.ROOT_URLCONF)
        if not hasattr(urls, "urlpatterns"):
            raise ImportError('urlpatterns in urls is underfined.')
        self._urlpatterns = getattr(urls, "urlpatterns", [])

    def _callback_from_patterns(self, urlpatterns, pattern, regex = None):
        for u in urlpatterns:
            p_pattern = u.regex.pattern
            if regex:
                if p_pattern.startswith("^"):
                    p_pattern = regex + p_pattern[1:]
            if isinstance(u, RegexURLPattern) and re.match(p_pattern, pattern):
                return u.callback
            elif isinstance(u, RegexURLResolver) and pattern.startswith(p_pattern[1:]):
                return self._callback_from_patterns(u.urlpatterns, pattern, p_pattern)
        return None
    
    def callback(self, pattern):
        return self._callback_from_patterns(self._urlpatterns, pattern)
                

urlpatterns = LazyUrls()