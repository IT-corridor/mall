import os
import json
from .base import *
from .mailgun import *
from .rq_settings import *

config_path = os.path.join(BASE_DIR, 'config.json')
with open(config_path, 'r') as f:
    data = json.load(f)
SECRET_KEY = data['SECRET_KEY']

# RESOURCE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'a-static')

DEBUG = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'rest_framework',
    'rest_framework_swagger',
    'settings',
    'account',
    'catalog',
    'vendor_admin',
    'visitor',
    'snapshot',
    'utils',
    'django_rq',
    'corsheaders',
]

ALLOWED_HOSTS = ['.atyichu.com']

USE_X_FORWARDED_HOST = True
ADMINS = ((data['ADMIN'], data['ADMIN_EMAIL']),
          ('Dan', 'dan8931484@gmail.com'))   # hide


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# NEED to set a user and a password before deployment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': data['DB_NAME'],
        'USER': data['DB_USER'],
        'PASSWORD': data['DB_PASSWORD'],
        'HOST': 'rm-2ze851zi768k30shf.pg.rds.aliyuncs.com',
        'PORT': 3433,
        'TEST': {
            'NAME': 'atyichu_mall_test',
        }
        #'ATOMIC_REQUESTS': True,
    }
}
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
        'OPTIONS': {
            'DB': 0,
        },
    },
    'pending': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
        'OPTIONS': {
            'DB': 1,
        },
    },
    'pending_phones': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
        'OPTIONS': {
            'DB': 2,
        },
    },
    'verify_phones': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
        'OPTIONS': {
            'DB': 3,
        },
    },
    'redis-cache': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
        'OPTIONS': {
            'DB': 4,
        },
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
# Static files will be serving by the proxy server
# and it have to be outside of the project root

STATIC_ROOT = os.path.join(RESOURCE_DIR, 'static')
MEDIA_ROOT = os.path.join(RESOURCE_DIR, 'media')

EMAIL_BACKEND = 'django_mailgun_mime.backends.MailgunMIMEBackend'
MAILGUN_API_KEY = data['MAILGUN_API_KEY']
MAILGUN_DOMAIN_NAME = data['MAILGUN_DOMAIN_NAME']

DEFAULT_FROM_EMAIL = 'post@atyichu.com'
SERVER_EMAIL = 'beholder@atyichu.com'

WEIXIN_APP_ID = data['WEIXIN_APP_ID']
WEIXIN_SECRET = data['WEIXIN_SECRET']
WEIXIN_QR_APP_ID = data['WEIXIN_QR_APP_ID']
WEIXIN_QR_SECRET = data['WEIXIN_QR_SECRET']

IMAGGA_KEY = data['IMAGGA_KEY']
IMAGGA_SECRET = data['IMAGGA_SECRET']
IMAGGA_LANG = 'zh_chs'

TAO_SMS_KEY = data['TAO_SMS_KEY']
TAO_SMS_SECRET = data['TAO_SMS_SECRET']

# CORS
CORS_ORIGIN_WHITELIST = ('atyichu.com',
                         'www.atyichu.com',
                         'store.atyichu.com',
                         'weixin.qq.com',
                         'open.weixin.qq.com',
                         )
CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_DOMAIN = ".atyichu.com"
SESSION_COOKIE_DOMAIN = ".atyichu.com"