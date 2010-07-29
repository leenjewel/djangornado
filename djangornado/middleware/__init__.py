# -*- coding: utf-8 -*-
from threading import Lock

from djangornado.core import exceptions
from djangornado.conf import settings
from djangornado.utils.importlib import import_module

class _Middleware(object):

    def __init__(self):
        self._request_middleware = None
        self._response_middleware = None
        self._exception_middleware = None

        self._init_lock = Lock()

    def _load_middleware(self):
        '''
        Populate middleware lists from settings['middleware']['classes'].
        Must be called after the environment is fixed (see __call__).
        '''
        self._response_middleware = []
        self._exception_middleware = []

        request_middleware = []
        for middleware_path in settings.MIDDLEWARE_CLASSES:
            try:
                dot = middleware_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '%s isn\'t a middleware module' % middleware_path
            mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]
            try:
                mod = import_module(mw_module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing middleware %s: "%s"' % (mw_module, e)
            try:
                mw_class = getattr(mod, mw_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname)

            try:
                mw_instance = mw_class()
            except exceptions.MiddlewareNotUsed:
                continue

            if hasattr(mw_instance, 'process_request'):
                request_middleware.append(mw_instance.process_request)
            if hasattr(mw_instance, 'process_response'):
                self._response_middleware.insert(0, mw_instance.process_response)
            if hasattr(mw_instance, 'process_exception'):
                self._exception_middleware.insert(0, mw_instance.process_exception)
        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._request_middleware = request_middleware


    def _check_install(self):
        if self._request_middleware is None:
            self._init_lock.acquire()
            # Check that middleware is still uninitialised.
            if self._request_middleware is None:
                self._load_middleware()
            self._init_lock.release()

    def _get_request_middleware(self):
        self._check_install()
        return self._request_middleware
    request_middleware = property(_get_request_middleware)

    def _get_response_middleware(self):
        self._check_install()
        return self._response_middleware
    response_middleware = property(_get_response_middleware)

    def _get_exception_middleware(self):
        self._check_install()
        return self._exception_middleware
    exception_middleware = property(_get_exception_middleware)

middleware = _Middleware()
