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
            if not settings_path: # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            # NOTE: This is arguably an EnvironmentError, but that causes
            # problems with Python's interactive help.
            raise ImportError('No settings file path given, because environment variable %s is undefined.' % ENVIRONMENT_VARIABLE)
        self.settings_module = import_module(settings_path)
        self.settings_dict = self.settings_module.__dict__
        super(LazySettings, self).__init__(self.settings_dict.items())
    
    def __getattr__(self, attr):
        return self.get(attr)

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
        has_resolver = False
        for u in urlpatterns:
            if isinstance(u, RegexURLPattern):
                if regex:
                    p_pattern = u.regex.pattern
                    if p_pattern.startswith('^'):
                        p_pattern = p_pattern[1:]
                    if re.match(regex+p_pattern, pattern):
                        return u.callback
                elif u.regex.match(pattern):
                    return u.callback
            elif has_resolver is False:
                has_resolver = True
        if has_resolver:
            for u in urlpatterns:
                if isinstance(u, RegexURLResolver):
                    return self._callback_from_patterns(u.urlpatterns, pattern, u.regex.pattern)
        return None
    
    def callback(self, pattern):
        return self._callback_from_patterns(self._urlpatterns, pattern)
                

urlpatterns = LazyUrls()