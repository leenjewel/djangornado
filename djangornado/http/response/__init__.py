# -*- coding:utf-8 -*-

import simplejson as json

class RenderResponse(object):
    def __init__(self, template, context, request_context = None):
        self.template = template
        self.context = context

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