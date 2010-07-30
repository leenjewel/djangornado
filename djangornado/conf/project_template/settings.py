# -*- coding:utf-8 -*-
import os, sys

DEBUG = True

BASEURL = 'http://'

BASEROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

MEDIA_ROOT = BASEROOT + "/static"

MEDIA_URL = BASEURL+"/static/ap/static"

SECRET_KEY = ''

MIDDLEWARE_CLASSES = (
    
)

ROOT_URLCONF = 'apps.urls'

template_path = BASEROOT + "/apps/templates"

SESSION_COOKIE_SECURE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = None
SESSION_ENGINE = 'libs.ttsession.tokyo'
