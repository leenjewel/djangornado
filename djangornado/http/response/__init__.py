# -*- coding:utf-8 -*-

import simplejson as json
from djangornado.conf import settings
from djangornado.utils.importlib import import_module
from djangornado.core.exceptions import ImproperlyConfigured

class RenderResponse(object):
    def __init__(self, template, context = {}, request_context = None):
        self.template = template
        self.context = context
        self._load_context()
    
    def _load_context(self):
        if hasattr(settings, "TEMPLATE_CONTEXT_PROCESSORS"):
            for path in settings.TEMPLATE_CONTEXT_PROCESSORS:
                i = path.rfind('.')
                module, attr = path[:i], path[i+1:]
                try:
                    mod = import_module(module)
                except ImportError, e:
                    raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
                try:
                    func = getattr(mod, attr)
                except AttributeError:
                    raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
                self.context.update(func())
        return None

class HttpResponse(object):
    def __init__(self, response):
        self.response = response
    
    def __str__(self):
        if isinstance(self.response, unicode):
            self.response = self.response.encode("utf-8")
        if not isinstance(self.response, str):
            self.response = str(self.response)
        return self.response

class JsonResponse(object):
    def __init__(self, response):
        self.response = response
    
    def __str__(self):
        return json.dumps(self.response, indent = 4)