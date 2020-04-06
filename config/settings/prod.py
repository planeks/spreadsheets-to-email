from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import dj_database_url
from .base import *

if config("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=config("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

DEBUG = config("DEBUG", default=False)

ALLOWED_HOSTS = [
    config("DOMAIN"),
]

CACHES = {
    "default": {"BACKEND": "redis_cache.RedisCache", "LOCATION": config("REDIS_URL"),}
}

SECRET_KEY = config("SECRET_KEY")

# Database url
# Please check https://github.com/jacobian/dj-database-url to understand how to use it
DATABASES = {}

DATABASES["default"] = dj_database_url.config(default=config("DATABASE_URL"))

HEROKU = config("HEROKU")
if HEROKU:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
