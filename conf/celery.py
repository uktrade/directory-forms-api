from __future__ import absolute_import, unicode_literals

import os
from ssl import CERT_NONE

from celery import Celery
from celery.schedules import crontab
from dbt_copilot_python.celery_health_check import healthcheck
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

app = Celery("forms-api")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "send_gov_notify_bulk_email_every_15_mins": {
        "task": "submission.tasks.send_gov_notify_bulk_email",
        "schedule": crontab(minute="*/15"),
    },
}

if settings.FEATURE_REDIS_USE_SSL:
    ssl_conf = {
        "ssl_cert_reqs": CERT_NONE,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }
    app.conf.broker_use_ssl = ssl_conf
    app.conf.redis_backend_use_ssl = ssl_conf

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# DBT celery healthcheck config
app = healthcheck.setup(app)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
