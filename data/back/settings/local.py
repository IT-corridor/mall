from .base import *
from .local_rq_settings import *

SECRET_KEY = 'g%vsow(2i!3k_*+o=$1rp5hm=9+ivwpqbk0grvs8=pgo=4c$vh'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    #'debug_toolbar',
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

LANGUAGE_CODE = 'en-US'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

    }
}

STATIC_ROOT = os.path.join(RESOURCE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(RESOURCE_DIR, 'static_dev'),)
MEDIA_ROOT = os.path.join(RESOURCE_DIR, 'media')
LOCALE_PATHS = (os.path.join(RESOURCE_DIR, 'locale'),)

# IMPORTANT, CACHE:

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 0,
        },
    },
    'pending': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 1,
        },
    },
    'pending_phones': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 2,
        },
    },
    'verify_phones': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 3,
        },
    },
    'redis-cache': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 4,
        },
    }
}

#SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
#SESSION_COOKIE_DOMAIN = ['127.0.0.1']
SESSION_COOKIE_HTTPONLY = False
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp', 'email')

WEIXIN_APP_ID = 'wx923ca88a0f604e90'
WEIXIN_SECRET = '392aad4be93c5bf2a535d5b932186b7b'
WEIXIN_QR_APP_ID = 'wx6ad4cd8923e9ea5e'
WEIXIN_QR_SECRET = 'a385ba5adf67452659c3ff7615e86198'

IMAGGA_KEY = 'acc_60524b660772546'
IMAGGA_SECRET = 'b8a7133f5990d04038ce468c7321d82c'
IMAGGA_LANG = 'zh_chs'

TAO_SMS_KEY = '23438643'
TAO_SMS_SECRET = '785f1713c9472a73596336a9f5e3eeeb'

CORS_ORIGIN_WHITELIST = ('127.0.0.1:8001', '127.0.0.1:8002')
CORS_ALLOW_CREDENTIALS = True
