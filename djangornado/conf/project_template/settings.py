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
    'djangornado.contrib.sessions.middleware.SessionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (

)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = BASEROOT + "/templates"

SESSION_COOKIE_NAME = 'sessionid'
