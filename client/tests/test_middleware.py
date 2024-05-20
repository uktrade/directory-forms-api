import pytest
import sigauth.helpers
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed

from client.tests import factories
from core.tests.test_views import reload_urlconf

SIGNATURE_CHECK_REQUIRED_MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'client.middleware.SignatureCheckMiddleware',
]


def test_signature_check_middleware_admin(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    response = admin_client.get(reverse('admin:auth_user_changelist'))

    assert response.status_code == 200


def test_signature_check_middleware_healthcheck(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    response = admin_client.get(reverse('healthcheck:ping'))

    assert response.status_code == 200


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'sender_id', ('fake-sender', '5db88d67-fbc7-4406-9b67-ec0e0138e634')
)
def test_signature_check_middleware_unknown_client(
    admin_client, settings, sender_id
):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret='fake-secret',
        sender_id=sender_id,
    )
    headers = signer.get_signature_headers(
        url=url,
        body=None,
        method='get',
        content_type='text/plain',
    )
    with pytest.raises(AuthenticationFailed):
        response = admin_client.get(
            url, {}, HTTP_X_SIGNATURE=headers[signer.header_name]
        )
        assert response.status_code == 401


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
def test_signature_check_middleware_inactive_client(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    client_model_instance = factories.ClientFactory(
        name='test',
        is_active=False,
        access_key='test-key',
    )
    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret='test-key',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url=url,
        body=None,
        method='get',
        content_type='text/plain',
    )
    with pytest.raises(AuthenticationFailed):
        response = admin_client.get(
            url, {}, HTTP_X_SIGNATURE=headers[signer.header_name]
        )
        assert response.status_code == 401


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
def test_signature_check_middleware_valid_client(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    client_model_instance = factories.ClientFactory(
        name='test',
        access_key='test-key',
    )
    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret='test-key',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url=url,
        body=None,
        method='get',
        content_type='text/plain',
    )
    response = admin_client.get(
        url, {}, HTTP_X_SIGNATURE=headers[signer.header_name]
    )

    assert response.status_code == 200


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
def test_signature_check_middleware_incorrect_secret(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE

    client_model_instance = factories.ClientFactory(
        name='test',
        access_key='test-key',
    )
    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret='incorrect-secret',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url=url,
        body=None,
        method='get',
        content_type='text/plain',
    )
    with pytest.raises(AuthenticationFailed):
        response = admin_client.get(
            url, {}, HTTP_X_SIGNATURE=headers[signer.header_name]
        )
        assert response.status_code == 401


def test_signature_check_middleware_admin_login(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE
    response = admin_client.get(reverse('admin:login'))

    assert response.status_code == 302


def test_signature_check_middleware_authbroker_login(admin_client, settings):
    settings.MIDDLEWARE = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()

    response = admin_client.get(reverse('authbroker_client:login'))

    assert response.status_code == 302
