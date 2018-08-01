import pytest
import sigauth.helpers

from django.urls import reverse

from client.tests import factories


SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'client.middleware.SignatureCheckMiddleware',
]


def test_signature_check_middleware_admin(admin_client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

    response = admin_client.get(reverse('admin:auth_user_changelist'))

    assert response.status_code == 200


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'sender_id', ('fake-sender', '5db88d67-fbc7-4406-9b67-ec0e0138e634')
)
def test_signature_check_middleware_unknown_client(
    admin_client, settings, sender_id
):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

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

    response = admin_client.get(
        url, {}, HTTP_X_SIGNATURE=headers[signer.header_name]
    )

    assert response.status_code == 401


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
def test_signature_check_middleware_inactive_client(admin_client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

    client_model_instance = factories.ClientFactory(
        name='test',
        is_active=False,
    )
    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret=client_model_instance.access_key,
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

    assert response.status_code == 401


@pytest.mark.urls('client.tests.urls')
@pytest.mark.django_db
def test_signature_check_middleware_valid_client(admin_client, settings):
    settings.MIDDLEWARE_CLASSES = SIGNATURE_CHECK_REQUIRED_MIDDLEWARE_CLASSES

    client_model_instance = factories.ClientFactory(name='test')
    url = reverse('test_view')

    signer = sigauth.helpers.RequestSigner(
        secret=client_model_instance.access_key,
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
