import pytest
import sigauth

from client import authentication
from client.tests import factories


@pytest.mark.django_db
def test_client_sender_authentication_ok(rf):
    authenticator = authentication.ClientSenderIdAuthentication()

    client_model_instance = factories.ClientFactory(
        name='test',
        access_key='test-key',
    )

    signer = sigauth.helpers.RequestSigner(
        secret='test-key',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url='/',
        body=None,
        method='get',
        content_type='text/plain',
    )
    request = rf.get('/', HTTP_X_SIGNATURE=headers[signer.header_name])

    client, _ = authenticator.authenticate(request)

    assert client == client_model_instance


@pytest.mark.django_db
def test_client_sender_authentication_authorisation_ok(rf):
    authenticator = authentication.ClientSenderIdAuthentication()

    client_model_instance = factories.ClientFactory(
        name='test',
        access_key='test-key',
    )

    signer = sigauth.helpers.RequestSigner(
        secret='test-key',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url='/',
        body=None,
        method='get',
        content_type='text/plain',
    )
    request = rf.get('/', HTTP_AUTHORIZATION=headers[signer.header_name])

    client, _ = authenticator.authenticate(request)

    assert client == client_model_instance
