from rest_framework import authentication, exceptions

from mohawk.util import parse_authorization_header

from client import helpers


class ClientSenderIdAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        header = request.META.get(helpers.RequestSignatureChecker.header_name)
        parsed_header = parse_authorization_header(header)
        return self.authenticate_credentials(parsed_header['id'])

    def authenticate_credentials(self, client_identifier):
        try:
            client = helpers.lookup_client(client_identifier)
        except LookupError as error:
            raise exceptions.AuthenticationFailed(error)
        return (client, None)
