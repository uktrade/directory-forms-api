import pytest
import sys
from importlib import import_module, reload

from django.conf import settings
from django.urls import clear_url_caches
from django.urls import reverse
from unittest import mock
from rest_framework.test import APIClient

from core.pingdom.services import DatabaseHealthCheck
from client.tests.factories import ClientFactory


URL = 'http://testserver' + reverse('pingdom')


@pytest.fixture
def user():
    return ClientFactory()


@pytest.fixture
def api_client(user):
    client = APIClient()
    settings.SIGAUTH_URL_NAMES_WHITELIST = ['pingdom']
    client.force_authenticate(user=user)
    return client


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)


def test_force_staff_sso(client):
    """Test that URLs and redirects are in place."""
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    settings.AUTHBROKER_CLIENT_ID = 'debug'
    settings.AUTHBROKER_CLIENT_SECRET = 'debug'
    settings.AUTHBROKER_URL = 'https://test.com'
    reload_urlconf()

    assert reverse('authbroker_client:login') == '/auth/login/'
    assert reverse('authbroker_client:callback') == '/auth/callback/'
    response = client.get(reverse('admin:login'))
    assert response.status_code == 302
    assert response.url == '/auth/login/'

    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = False
    reload_urlconf()


@pytest.mark.django_db
def test_pingdom_database_healthcheck_ok(api_client):
    response = api_client.get(
        URL,
    )
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(DatabaseHealthCheck, 'check')
def test_pingdom_database_healthcheck_false(mock_database_check, api_client):
    mock_database_check.return_value = (
        False,
        'Database Error',
    )

    response = api_client.get(
        URL,
    )
    assert response.status_code == 500
