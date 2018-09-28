import directory_healthcheck.views

from django.conf.urls import url, include
from django.contrib import admin

import healthcheck.views
import submission.views


admin.autodiscover()


healthcheck_urls = [
    url(
        r'^database/$',
        healthcheck.views.DatabaseAPIView.as_view(),
        name='database'
    ),
    url(
        r'^ping/$',
        directory_healthcheck.views.PingView.as_view(),
        name='ping'
    ),
    url(
        r'^sentry/$',
        directory_healthcheck.views.SentryHealthcheckView.as_view(),
        name='sentry'
    ),
]


urlpatterns = [
    url(
        r'^api/healthcheck/',
        include(healthcheck_urls, namespace='healthcheck')
    ),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^api/submission/$',
        submission.views.SubmissionCreateAPIView.as_view(),
        name='submission'
    ),
]
