import directory_healthcheck.views

from django.conf.urls import url, include
from django.contrib import admin

import healthcheck.views
import submission.views
import testapi.views


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

api_urls = [
    url(
        r'^submission/$',
        submission.views.SubmissionCreateAPIView.as_view(),
        name='submission'
    ),
]

testapi_urls = [
    url(
        r'^submission-by-email/(?P<email_address>.*)/$',
        testapi.views.SubmissionTestAPIView.as_view(),
        name='submission_by_email',
    ),
]

urlpatterns = [
    url(
        r'^api/healthcheck/',
        include(
            healthcheck_urls, namespace='healthcheck', app_name='healthcheck'
        )
    ),
    url(
        r'^api/',
        include(api_urls, namespace='api', app_name='api')
    ),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^testapi/',
        include(testapi_urls, namespace='testapi', app_name='testapi')
    ),
]
