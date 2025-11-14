import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    send_default_pii=True
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

# Application definition
INSTALLED_APPS = [
    'corsheaders',  # CORS support
    'home',
    'articles',
    'conditions',
    'drugs', #Added drugs app
    'search',
    'news',
    'social_media', # Added social media app
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    # 'wagtailseo',  # Package not available
    'wagtail.api.v2',
    'wagtail_localize',
    'wagtail_localize.locales',
    'rosetta',  # Add Rosetta
    'modelcluster',
    'taggit',
    'rest_framework',
    'api',  # Custom API app
    'remedies', # Added remedies app

    'django.conf.locale',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_extensions',

]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.replit\.dev$",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # For development only

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware - must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'healthinfo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'healthinfo.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
]

WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = [
    ('en', "English"),
    ('hi', "Hindi"),
]

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Wagtail settings
WAGTAIL_SITE_NAME = "Health Info CMS"
WAGTAILADMIN_BASE_URL = 'http://localhost:8001'

# Search - Using Meilisearch
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    },
    'meilisearch': {
        'BACKEND': 'wagtail.search.backends.database',
        'AUTO_UPDATE': True,
        'TIMEOUT': 10,
    }
}

# Meilisearch configuration
MEILISEARCH_HOST = os.getenv('MEILISEARCH_HOST', 'http://127.0.0.1:7700')
MEILISEARCH_API_KEY = os.getenv('MEILISEARCH_API_KEY', 'healthinfo_master_key_2024')

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'http://localhost:8001'

# API settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Wagtail API settings
WAGTAILAPI_LIMIT_MAX = 50

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'