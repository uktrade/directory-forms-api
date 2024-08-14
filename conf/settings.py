import os
from typing import Any, Dict

import dj_database_url
import sentry_sdk
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .utils import strip_password_data
from conf.env import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.debug

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
    'django_json_widget',
    'rest_framework',
    'health_check.db',
    'health_check.cache',
    'directory_healthcheck',
    'core.apps.CoreConfig',
    'submission.apps.SubmissionConfig',
    'client.apps.ClientConfig',
    'testapi.apps.TestApiConfig',
    'authbroker_client',
    'django_celery_beat',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.AdminPermissionCheckMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'client.middleware.SignatureCheckMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

REDIS_URL = env.redis_url

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {'default': dj_database_url.config(default=env.database_url)}

# Caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # separate to REDIS_URL as needs to start with 'rediss' for SSL
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
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
STATIC_HOST = env.static_host
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = env.staticfiles_storage

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


# SSO config
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.feature_enforce_staff_sso_enabled
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'authbroker_client.backends.AuthbrokerBackend'
    ]

    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('admin:index')

# authbroker config
AUTHBROKER_URL = env.staff_sso_authbroker_url
AUTHBROKER_CLIENT_ID = env.authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.secret_key

# OpenAPI

FEATURE_OPENAPI_ENABLED = env.feature_openapi_enabled
SPECTACULAR_SETTINGS = {
    'TITLE': 'Directory Forms API spec',
    'DESCRIPTION': 'Directory Forms API - the Department for Business and Trade (DBT)',
    'VERSION': os.environ.get('GIT_TAG', 'dev'),
}

# DRF
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# Logging for development
if DEBUG:
    LOGGING: Dict[str, Any] = {
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
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'asim_formatter': {
                '()': ASIMFormatter,
            },
            'simple': {
                'style': '{',
                'format': '{asctime} {levelname} {message}',
            },
        },
        'handlers': {
            'asim': {
                'class': 'logging.StreamHandler',
                'formatter': 'asim_formatter',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['asim'],
                'level': 'INFO',
                'propagate': False,
            },
            'sentry_sdk': {'level': 'ERROR', 'handlers': ['asim'], 'propagate': False},
        },
    }

# Sentry
if env.sentry_dsn:
    sentry_sdk.init(
        dsn=env.sentry_dsn,
        environment=env.sentry_environment,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.sentry_enable_tracing,
        traces_sample_rate=env.sentry_traces_sample_rate,
    )

# Elastic APM logging
ELASTIC_APM_ENABLED = env.elastic_apm_enabled
if ELASTIC_APM_ENABLED:
    ELASTIC_APM = {
        'SERVICE_NAME': env.service_name,
        'SECRET_TOKEN': env.elastic_apm_secret_token,
        'SERVER_URL': env.elastic_apm_urL,
        'ENVIRONMENT': env.environment,
        'SERVER_TIMEOUT': env.elastic_apm_server_timeout,
    }
    INSTALLED_APPS.append('elasticapm.contrib.django')

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = env.session_cookie_domain
SESSION_COOKIE_NAME = 'directory_forms_api_admin_session_id'
SESSION_COOKIE_SECURE = env.session_cookie_secure
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.csrf_cookie_secure

# health check
DIRECTORY_HEALTHCHECK_TOKEN = env.health_check_token
DIRECTORY_HEALTHCHECK_BACKENDS = [
    # health_check.db.backends.DatabaseBackend and
    # health_check.cache.backends.CacheBackend are also registered in
    # INSTALLED_APPS's health_check.db and health_check.cache
]

# directory-signature-auth
SIGAUTH_URL_NAMES_WHITELIST = [
    'database',  # health check
    'ping',  # health check
    'pingdom',  # health check
    'activity-stream',  # activity stream
    'schema',
    'swagger-ui',
    'redoc',
]

# Zendesk
ZENDESK_SUBDOMAIN_DEFAULT = env.zendesk_subdomain
ZENDESK_SUBDOMAIN_EUEXIT = env.zendesk_subdomain_euexit
ZENDESK_CREDENTIALS = {
    ZENDESK_SUBDOMAIN_DEFAULT: {
        'token': env.zendesk_token,
        'email': env.zendesk_email,
        'custom_field_id': env.zendesk_custom_field_id,
    },
    ZENDESK_SUBDOMAIN_EUEXIT: {
        'token': env.zendesk_token_euexit,
        'email': env.zendesk_email_euexit,
        'custom_field_id': env.zendesk_custom_field_id_euexit,
    },
}

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend'
}
EMAIL_BACKED_CLASS_NAME = env.email_backend_class_name
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.email_host
EMAIL_PORT = env.email_port
EMAIL_HOST_USER = env.email_host_user
EMAIL_HOST_PASSWORD = env.email_host_password
EMAIL_USE_TLS = env.email_use_tls
DEFAULT_FROM_EMAIL = env.default_from_email

# Celery
# separate to REDIS_URL as needs to start with 'redis' and SSL conf
# is in conf/celery.py
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None
FEATURE_REDIS_USE_SSL = env.feature_redis_use_ssl
CELERY_TASK_ALWAYS_EAGER = env.celery_always_eager

# Gov UK Notify
GOV_NOTIFY_API_KEY = env.gov_notify_api_key
BUY_FROM_UK_ENQUIRY_TEMPLATE_ID = env.buy_from_uk_enquiry_template_id
BUY_FROM_UK_EMAIL_ADDRESS = env.buy_from_uk_email_address
# default UUID value is id of email listed on notification service
BUY_FROM_UK_REPLY_TO_EMAIL_ADDRESS = env.buy_from_uk_reply_to_email_address
# Separate key to allow PDF viewing. In prod this can be live key
GOV_NOTIFY_LETTER_API_KEY = env.gov_notify_letter_api_key


# Test API
FEATURE_TEST_API_ENABLED = env.feature_test_api_enabled

# Activity Stream API
ACTIVITY_STREAM_ACCESS_KEY_ID = env.activity_stream_access_key_id
ACTIVITY_STREAM_SECRET_ACCESS_KEY = env.activity_stream_secret_access_key

# Ratelimit config
# Set RATELIMIT_ENABLE to enable/disable
# the number of requests per unit time allowed in (s/m/h/d)
RATELIMIT_RATE = env.ratelimit_rate

# When filtering submissions to action (i.e. send email, send letter, send to gov.notify), how many hours
# should we filter?
SUBMISSION_FILTER_HOURS = env.submission_filter_hours
