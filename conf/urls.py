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
        name='submissions_by_email',
    ),
    url(
        r'^test-senders/$',
        testapi.views.SendersTestAPIView.as_view(),
        name='delete_test_senders',
    ),
    url(
        r'^test-submissions/$',
        testapi.views.SubmissionsTestAPIView.as_view(),
        name='delete_test_submissions',
    ),
]


urlpatterns = [
    url(r'^api/healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    url(r'^api/', include((api_urls, 'api'), namespace='api')),
    url(r'^admin/', admin.site.urls),
    url(r'^testapi/', include((testapi_urls, 'testapi'), namespace='testapi')),
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
