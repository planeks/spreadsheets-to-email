from .base import *

ALLOWED_HOSTS = ['*']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60,
        'LOCATION': 'unique-snowflake',
    }
}

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<SECRET KEY>'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test.sqlite3'),
    }
}