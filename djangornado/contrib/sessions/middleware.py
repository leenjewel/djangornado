# -*- coding:utf-8 -*-
'''
Created on 2010-7-29

@author: leenjewel
'''

from djangornado.utils.importlib import import_module
from djangornado.conf import settings

class SessionMiddleware(object):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        if settings.SESSION_COOKIE_SECURE:
            session_key = self.get_secure_cookie(settings.SESSION_COOKIE_NAME)
        else:
            session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        request.session = engine.SessionStore(session_key)
    
    def process_response(self, request):
        try:
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    expires_days = None
                else:
                    expires_days = request.session.get_expires_days()
                # Save the session data and refresh the client cookie.
                request.session.save()
                if settings.SESSION_COOKIE_SECURE:
                    request.set_secure_cookie(settings.SESSION_COOKIE_NAME,
                            request.session.session_key, expires_days = expires_days,
                            domain = settings.SESSION_COOKIE_DOMAIN,
                            path = "/")
                else:
                    request.set_cookie(settings.SESSION_COOKIE_NAME,
                            request.session.session_key, expires_days = expires_days,
                            domain = settings.SESSION_COOKIE_DOMAIN,
                            path = "/")