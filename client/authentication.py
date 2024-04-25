import logging

from rest_framework import authentication, exceptions

from mohawk.util import parse_authorization_header

from client.helpers import RequestSignatureChecker, lookup_client


logger = logging.getLogger(__name__)


class ClientSenderIdAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        # Check using x-sig or auth sig
        if RequestSignatureChecker.header_name in request.META:
            header = request.META.get(RequestSignatureChecker.header_name)
        else:
            header = request.META.get(RequestSignatureChecker.authorisation_header_name)

        parsed_header = parse_authorization_header(header)
        return self.authenticate_credentials(parsed_header['id'])

    def authenticate_credentials(self, client_identifier):
        try:
            client = lookup_client(client_identifier)
        except LookupError as error:
            logger.error(exceptions.AuthenticationFailed(error))
            raise exceptions.AuthenticationFailed()
        return (client, None)
