import directory_healthcheck.views

from django.urls import re_path, include, reverse_lazy
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings

import submission.views
from activitystream.views import ActivityStreamView
import testapi.views


admin.autodiscover()


healthcheck_urls = [
    re_path(
        r'^$',
        directory_healthcheck.views.HealthcheckView.as_view(),
        name='healthcheck'
    ),
    re_path(
        r'^ping/$',
        directory_healthcheck.views.PingView.as_view(),
        name='ping'
    ),
]

api_urls = [
    re_path(
        r'^submission/$',
        submission.views.SubmissionCreateAPIView.as_view(),
        name='submission'
    ),
    re_path(
        r'^delete-submissions/(?P<email_address>.*)$',
        submission.views.SubmissionDestroyAPIView.as_view(),
        name='delete_submission',
    ),
]

testapi_urls = [
    re_path(
        r'^submissions-by-email/(?P<email_address>.*)/$',
        testapi.views.SubmissionsTestAPIView.as_view(),
        name='submissions_by_email',
    ),
    re_path(
        r'^test-senders/$',
        testapi.views.SendersTestAPIView.as_view(),
        name='delete_test_senders',
    ),
    re_path(
        r'^test-submissions/$',
        testapi.views.SubmissionsTestAPIView.as_view(),
        name='delete_test_submissions',
    ),
]

urlpatterns = [
    re_path(
        r'^api/healthcheck/',
        include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')
    ),

    re_path(r'^api/', include((api_urls, 'api'), namespace='api')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^testapi/', include((testapi_urls, 'testapi'), namespace='testapi')),
    re_path(r'^activity-stream/v1/', ActivityStreamView.as_view(), name='activity-stream'),
]

authbroker_urls = [
    re_path(
        r'^admin/login/$',
        RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True, )
    ),
    re_path('^auth/', include('authbroker_client.urls')),
]

if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    urlpatterns = [re_path('^', include(authbroker_urls))] + urlpatterns
