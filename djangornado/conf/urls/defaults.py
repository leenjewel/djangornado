# -*- coding:utf-8 -*-
'''
Created on 2010-7-29

@author: leenjewel
'''

from djangornado.core.urlresolvers import RegexURLPattern
from djangornado.core.exceptions import ImproperlyConfigured

__all__ = ['include', 'patterns', 'url']

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

def include(arg, namespace=None, app_name=None):
    if isinstance(arg, tuple):
        # callable returning a namespace hint
        if namespace:
            raise ImproperlyConfigured('Cannot override the namespace for a dynamic module that provides a namespace')
        urlconf_module, app_name, namespace = arg
    else:
        # No namespace hint - use manually provided namespace
        urlconf_module = arg
    return (urlconf_module, app_name, namespace)

def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list

def url(regex, view, kwargs=None, name=None, prefix=''):
    if isinstance(view, basestring):
        if not view:
            raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
        if prefix:
            view = prefix + '.' + view
    return RegexURLPattern(regex, view, kwargs, name)