import sigauth.middleware
import sigauth.helpers

from client import helpers


class SignatureCheckMiddleware(sigauth.middleware.SignatureCheckMiddlewareBase):
    secret = ''

    def __init__(self, *args, **kwargs):
        self.request_checker = helpers.RequestSignatureChecker(self.secret)
        super().__init__(*args, **kwargs)

    def should_check(self, request):
        if request.resolver_match.namespace in [
            'admin', 'healthcheck', 'authbroker_client'
        ] or request.path_info.startswith('/admin/login'):
            return False
        return super().should_check(request)
