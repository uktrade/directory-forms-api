import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from core.tests.test_views import reload_urlconf

SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.AdminPermissionCheckMiddleware",
]


@pytest.fixture(autouse=False)
def admin_user():
    admin_user = User.objects.create_user("admin", "admin@test.com", "pass")
    admin_user.save()
    admin_user.is_staff = False
    admin_user.save()
    return admin_user


@pytest.mark.django_db
def test_authenticated_user_middleware_no_user(client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    response = client.get(reverse("admin:login"))

    assert response.status_code == 302
    assert response.url == reverse("authbroker_client:login")


@pytest.mark.django_db
def test_authenticated_user_middleware_authorised_no_staff(
    client, settings, admin_user
):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    client.force_login(admin_user)

    response = client.get(reverse("admin:login"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_user_middleware_authorised_with_staff(
    client, settings, admin_user
):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    admin_user.is_staff = True
    admin_user.save()
    client.force_login(admin_user)
    response = client.get(reverse("admin:login"))

    assert response.status_code == 302
