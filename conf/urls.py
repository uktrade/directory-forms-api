import directory_healthcheck.views

from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings

import submission.views
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

]

if settings.ENFORCE_STAFF_SSO_ON:
    urlpatterns = [
        url(
            r'^admin/login/$',
            RedirectView.as_view(url='/auth/login/', query_string=True, )
        ),
        url(
            '^auth/',
            include('authbroker_client.urls', namespace='authbroker', app_name='authbroker_client')
        ),
    ] + urlpatterns
