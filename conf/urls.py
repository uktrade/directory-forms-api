from django.conf.urls import url, include
from django.contrib import admin

import healthcheck.views
import core.views


admin.autodiscover()


urlpatterns = [
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^api/v1/healthcheck/database/$',
        healthcheck.views.DatabaseAPIView.as_view(),
        name='health-check-database'
    ),
    url(
        r'^api/v1/healthcheck/ping/$',
        healthcheck.views.PingAPIView.as_view(),
        name='health-check-ping'
    ),
    url(
        r'^api/v1/generic-submit/$',
        core.views.FormSubmissionCreateAPIView.as_view(),
        name='generic-submit'
    ),


]
