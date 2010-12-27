# -*- coding:utf-8 -*-
'''
Created on 2010-7-29

@author: leenjewel
'''

import re
from djangornado.core.exceptions import ViewDoesNotExist, ImproperlyConfigured
from djangornado.utils.importlib import import_module
from djangornado.utils.functional import memoize

_callable_cache = {}

def get_callable(lookup_view, can_fail=False):
    if not callable(lookup_view):
        try:
            lookup_view = lookup_view.encode('ascii')
            mod_name, func_name = get_mod_func(lookup_view)
            if func_name != '':
                lookup_view = getattr(import_module(mod_name), func_name)
                if not callable(lookup_view):
                    raise AttributeError("'%s.%s' is not a callable." % (mod_name, func_name))
        except (ImportError, AttributeError):
            if not can_fail:
                raise
        except UnicodeEncodeError:
            pass
    return lookup_view
get_callable = memoize(get_callable, _callable_cache, 1)

def get_mod_func(callback):
    try:
        dot = callback.rindex('.')
    except ValueError:
        return callback, ''
    return callback[:dot], callback[dot+1:]

class RegexURLResolver(object):
    def __init__(self, urlconf_name):
        self.urlconf_name = urlconf_name
        if not isinstance(urlconf_name, basestring):
            self._urlconf_module = self.urlconf_name
    
    def set_regex(self, regex):
        self.regex = re.compile(regex, re.UNICODE)

    def _get_urlconf_module(self):
        try:
            return self._urlconf_module
        except AttributeError:
            self._urlconf_module = import_module(self.urlconf_name)
            return self._urlconf_module
    urlconf_module = property(_get_urlconf_module)

    def _get_url_patterns(self):
        patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
        try:
            iter(patterns)
        except TypeError:
            raise ImproperlyConfigured("The included urlconf %s doesn't have any patterns in it" % self.urlconf_name)
        return patterns
    urlpatterns = property(_get_url_patterns)

class RegexURLPattern(object):
    def __init__(self, regex, callback, default_args = None):
        self.regex = re.compile(regex, re.UNICODE)
        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback
        self.default_args = default_args or {}

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.regex.pattern)

    def add_prefix(self, prefix):
        if not prefix or not hasattr(self, '_callback_str'):
            return
        self._callback_str = prefix + '.' + self._callback_str

    def resolve(self, path):
        match = self.regex.search(path)
        if match:
            kwargs = match.groupdict()
            if kwargs:
                args = ()
                kwargs.update(self.default_args)
            else:
                args = match.groups()
        return self.callback, args, kwargs
    
    def _get_callback(self):
        if self._callback is not None:
            return self._callback
        try:
            self._callback = get_callable(self._callback_str)
        except ImportError, e:
            mod_name, _ = get_mod_func(self._callback_str)
            raise ViewDoesNotExist("Could not import %s. Error was: %s" % (mod_name, str(e)))
        except AttributeError, e:
            mod_name, func_name = get_mod_func(self._callback_str)
            raise ViewDoesNotExist("Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e)))
        return self._callback
    callback = property(_get_callback)