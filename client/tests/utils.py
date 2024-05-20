import sigauth

from . import factories


def sign_valid_client_hawk_header(url):
    client_model_instance = factories.ClientFactory(
        name='test',
        access_key='test-key',
    )

    signer = sigauth.helpers.RequestSigner(
        secret='test',
        sender_id=str(client_model_instance.identifier),
    )
    headers = signer.get_signature_headers(
        url=url,
        body=None,
        method='get',
        content_type='text/plain',
    )
    return headers[signer.header_name]


def sign_invalid_client_hawk_header():
    signer = sigauth.helpers.RequestSigner(
        secret='test',
        sender_id='1234',
    )
    headers = signer.get_signature_headers(
        url='/',
        body=None,
        method='get',
        content_type='text/plain',
    )
    return headers[signer.header_name]
