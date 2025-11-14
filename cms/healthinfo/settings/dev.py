from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-for-development'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    "https://*.replit.dev",
    "https://*.replit.dev:8000",
    "https://*.replit.dev:8001",
    "https://*.repl.co",
    "https://*.repl.co:8000",
    "https://*.repl.co:8001",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://0.0.0.0:8000",
    "http://0.0.0.0:8001",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.repl.co",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.repl.co:8000",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.repl.co:8001",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.replit.dev",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.replit.dev:8000",
    "https://586e18a3-c2c4-4db2-87d8-dd794d4524c6-00-8pr2h6pbve6y.sisko.replit.dev:8001",
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Disable security settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Cache (disabled for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

try:
    from .local import *
except ImportError:
    pass