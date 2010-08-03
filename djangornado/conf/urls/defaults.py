# -*- coding:utf-8 -*-
'''
Created on 2010-7-29

@author: leenjewel
'''

from djangornado.core.urlresolvers import RegexURLPattern, RegexURLResolver
from djangornado.core.exceptions import ImproperlyConfigured

__all__ = ['include', 'patterns', 'url']

def include(arg):
    if isinstance(arg, basestring):
        return RegexURLResolver(arg)
    raise TypeError("include function need a basestring args.")

def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list

def url(regex, view, prefix = ''):
    if isinstance(view, RegexURLResolver):
        view.set_regex(regex)
        return view
    if isinstance(view, basestring):
        if not view:
            raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
        if prefix:
            view = prefix + '.' + view
    return RegexURLPattern(regex, view)
