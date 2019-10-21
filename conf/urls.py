import directory_healthcheck.views

from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings

import submission.views
from activitystream.views import ActivityStreamView
import testapi.views


admin.autodiscover()


healthcheck_urls = [
    url(
        r'^$',
        directory_healthcheck.views.HealthcheckView.as_view(),
        name='healthcheck'
    ),
    url(
        r'^ping/$',
        directory_healthcheck.views.PingView.as_view(),
        name='ping'
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
        r'^submissions-by-email/(?P<email_address>.*)/$',
        testapi.views.SubmissionsTestAPIView.as_view(),
        name='submissions-by-email',
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
    url(r'^activity-stream/v1/', ActivityStreamView.as_view(), name='activity-stream'),
]

authbroker_urls = [
    url(
        r'^admin/login/$',
        RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True, )
    ),
    url('^auth/', include('authbroker_client.urls')),
]

if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    urlpatterns = [url('^', include(authbroker_urls))] + urlpatterns

