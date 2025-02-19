import directory_healthcheck.views
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

import submission.views
import testapi.views
from activitystream.views import (ActivityStreamDomesticHCSATFeedbackDataView,
                                  ActivityStreamView)
from core.views import PingDomView

admin.autodiscover()


healthcheck_urls = [
    re_path(
        r"^$", directory_healthcheck.views.HealthcheckView.as_view(), name="healthcheck"
    ),
    re_path(r"^ping/$", directory_healthcheck.views.PingView.as_view(), name="ping"),
]

api_urls = [
    re_path(
        r"^submission/$",
        submission.views.SubmissionCreateAPIView.as_view(),
        name="submission",
    ),
    re_path(
        r"^delete-submissions/(?P<email_address>.*)$",
        submission.views.SubmissionDestroyAPIView.as_view(),
        name="delete_submission",
    ),
]

api_v2_urls = [
    re_path(
        r"^gov-notify-bulk-email/$",
        submission.views.GovNotifyBulkEmailAPIView.as_view(),
        name="gov-notify-bulk-email",
    ),
    re_path(
        r"^hcsat-feedback-submission/$",
        submission.views.HCSatAPIView.as_view(),
        name="hcsat-feedback-submission",
    ),
]

testapi_urls = [
    re_path(
        r"^submissions-by-email/(?P<email_address>.*)/$",
        testapi.views.SubmissionsTestAPIView.as_view(),
        name="submissions_by_email",
    ),
    re_path(
        r"^test-senders/$",
        testapi.views.SendersTestAPIView.as_view(),
        name="delete_test_senders",
    ),
    re_path(
        r"^test-submissions/$",
        testapi.views.SubmissionsTestAPIView.as_view(),
        name="delete_test_submissions",
    ),
]

urlpatterns = [
    re_path(
        r"^api/healthcheck/",
        include((healthcheck_urls, "healthcheck"), namespace="healthcheck"),
    ),
    path("pingdom/ping.xml", PingDomView.as_view(), name="pingdom"),
    re_path(r"^api/", include((api_urls, "api"), namespace="api")),
    re_path(r"^api/v2/", include((api_v2_urls, "api_v2"), namespace="api_v2")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^testapi/", include((testapi_urls, "testapi"), namespace="testapi")),
    re_path(
        r"^activity-stream/v1/", ActivityStreamView.as_view(), name="activity-stream"
    ),
    re_path(
        r"^activity-stream/v2/",
        ActivityStreamDomesticHCSATFeedbackDataView.as_view(),
        name="activity-stream-hcsat",
    ),
]

authbroker_urls = [
    re_path(
        r"^admin/login/$",
        RedirectView.as_view(
            url=reverse_lazy("authbroker_client:login"),
            query_string=True,
        ),
    ),
    re_path("^auth/", include("authbroker_client.urls")),
]

if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    urlpatterns = [re_path("^", include(authbroker_urls))] + urlpatterns

if settings.FEATURE_OPENAPI_ENABLED:
    urlpatterns += [
        path("openapi/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "openapi/ui/",
            login_required(
                SpectacularSwaggerView.as_view(url_name="schema"),
                login_url="admin:login",
            ),
            name="swagger-ui",
        ),
        path(
            "openapi/ui/redoc/",
            login_required(
                SpectacularRedocView.as_view(url_name="schema"), login_url="admin:login"
            ),
            name="redoc",
        ),
    ]
