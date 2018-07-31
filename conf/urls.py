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
        r'^api/healthcheck/database/$',
        healthcheck.views.DatabaseAPIView.as_view(),
        name='health-check-database'
    ),
    url(
        r'^api/healthcheck/ping/$',
        healthcheck.views.PingAPIView.as_view(),
        name='health-check-ping'
    ),
    url(
        r'^api/submission/$',
        core.views.FormSubmissionCreateAPIView.as_view(),
        name='generic-submit'
    ),


]
