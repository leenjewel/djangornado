# -*- coding:utf-8 -*-
import os, sys

DEBUG = True

BASEURL = 'http://'

BASEROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

static_path = BASEROOT + "/static"

MEDIA_URL = BASEURL+"/static"

SECRET_KEY = ''

MIDDLEWARE_CLASSES = (
    'djangornado.contrib.sessions.middleware.SessionMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (

)

ROOT_URLCONF = 'urls'

template_path = BASEROOT + "/templates"

SESSION_COOKIE_SECURE = True
cookie_secret = ''
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = None
SESSION_ENGINE = ''
