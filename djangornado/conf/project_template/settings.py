# -*- coding:utf-8 -*-
import os, sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOCAL = False

if LOCAL:
    pass
else:
    BASEURL = 'http://fbanimaltest.haalee.com'
    CACHE_BACKEND = 'memcached://127.0.0.1:9989'
    APP_CACHE_BACKEND = ('memcached://127.0.0.1:9999',300)
    #tokyo cabinet * memory hash
    DBW_TT_SERVERS = [("127.0.0.1", 20001)]
    #tokyo cabinet .tch file hash
    TC_TT_SERVERS = [("127.0.0.1", 20002)]
    
BASEROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

SHARD_FILE_CONF_PASSWORD = "/home/leenjewel/FILEDB.dat"

SHARD_TT_CONF_PASSWORD = (
    '127.0.0.1:1978',
)

SHARD_MYSQL_CONF_PASSWORD = (
    ('leenjewel', 'leen6553', '127.0.0.1', 'snsEventFrameDB'),
)

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

CACHE_PRE = ''