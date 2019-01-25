import os

import dj_database_url

import environ

from directory_components.constants import IP_RETRIEVER_NAME_GOV_UK


env = environ.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'health_check.db',
    'health_check.cache',
    'directory_healthcheck',
    'raven.contrib.django.raven_compat',
    'core.apps.CoreConfig',
    'submission.apps.SubmissionConfig',
    'client.apps.ClientConfig',
    'testapi.apps.TestApiConfig',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'directory_components.middleware.IPRestrictorMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'client.middleware.SignatureCheckMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_CELERY_URL = VCAP_SERVICES['redis'][0]['credentials']['uri'].replace(
        'rediss://', 'redis://'
    )
else:
    REDIS_CELERY_URL = env.str('REDIS_CELERY_URL', '')


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# S3 storage does not use these settings, needed only for dev local storage
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# Sentry
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', ''),
}

# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'mohawk': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'requests': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'elasticsearch': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN', 'great.gov.uk')
SESSION_COOKIE_NAME = 'directory_forms_api_admin_session_id'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)

# Activity Stream
REMOTE_IP_ADDRESS_RETRIEVER = env.str(
    'REMOTE_IP_ADDRESS_RETRIEVER', IP_RETRIEVER_NAME_GOV_UK
)

# health check
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    # health_check.db.backends.DatabaseBackend and
    # health_check.cache.backends.CacheBackend are also registered in
    # INSTALLED_APPS's health_check.db and health_check.cache
]

# Admin restrictor
RESTRICT_ADMIN = env.bool('RESTRICT_ADMIN', False)
ALLOWED_ADMIN_IPS = env.list('ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list('ALLOWED_ADMIN_IP_RANGES', default=[])

# directory-signature-auth
SIGAUTH_URL_NAMES_WHITELIST = [
    'database',  # health check
    'ping',  # health check
]

# Zendesk
ZENDESK_SUBDOMAIN_DEFAULT = env.str('ZENDESK_SUBDOMAIN')
ZENDESK_SUBDOMAIN_EUEXIT = env.str('ZENDESK_SUBDOMAIN_EUEXIT')
ZENDESK_CREDENTIALS = {
    ZENDESK_SUBDOMAIN_DEFAULT: {
        'token': env.str('ZENDESK_TOKEN'),
        'email': env.str('ZENDESK_EMAIL'),
        'custom_field_id': env.str('ZENDESK_CUSTOM_FIELD_ID')
    },
    ZENDESK_SUBDOMAIN_EUEXIT: {
        'token': env.str('ZENDESK_TOKEN_EUEXIT'),
        'email': env.str('ZENDESK_EMAIL_EUEXIT'),
        'custom_field_id': env.str('ZENDESK_CUSTOM_FIELD_ID_EUEXIT')
    },
}

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend'
}
EMAIL_BACKED_CLASS_NAME = env.str('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL')

# Celery
# separate to REDIS_CACHE_URL as needs to start with 'redis' and SSL conf
# is in conf/celery.py
CELERY_BROKER_URL = REDIS_CELERY_URL
CELERY_RESULT_BACKEND = REDIS_CELERY_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None
FEATURE_REDIS_USE_SSL = env.bool('FEATURE_REDIS_USE_SSL', False)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_ALWAYS_EAGER', False)


# Gov UK Notify
GOV_NOTIFY_API_KEY = env.str('GOV_NOTIFY_API_KEY')

# ip-restrictor
IP_RESTRICTOR_SKIP_CHECK_ENABLED = env.bool(
    'IP_RESTRICTOR_SKIP_CHECK_ENABLED', False
)
IP_RESTRICTOR_SKIP_CHECK_SENDER_ID = env.str(
    'IP_RESTRICTOR_SKIP_CHECK_SENDER_ID', ''
)
IP_RESTRICTOR_SKIP_CHECK_SECRET = env.str(
    'IP_RESTRICTOR_SKIP_CHECK_SECRET', ''
)
IP_RESTRICTOR_REMOTE_IP_ADDRESS_RETRIEVER = env.str(
    'IP_RESTRICTOR_REMOTE_IP_ADDRESS_RETRIEVER',
    IP_RETRIEVER_NAME_GOV_UK
)
RESTRICT_ADMIN = env.bool('IP_RESTRICTOR_RESTRICT_IPS', False)
ALLOWED_ADMIN_IPS = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list(
    'IP_RESTRICTOR_ALLOWED_ADMIN_IP_RANGES', default=[]
)
RESTRICTED_APP_NAMES = env.list(
    'IP_RESTRICTOR_RESTRICTED_APP_NAMES', default=['admin']
)
if env.bool('IP_RESTRICTOR_RESTRICT_UI', False):
    # restrict all pages that are not in apps API, healthcheck, admin, etc
    RESTRICTED_APP_NAMES.append('')

# Test API
FEATURE_TEST_API_ENABLED = env.bool('FEATURE_TEST_API_ENABLED', False)
