from admin_ip_restrictor import middleware
import sigauth.middleware

from django.conf import settings

from core import helpers


class AdminIPRestrictorMiddleware(middleware.AdminIPRestrictorMiddleware):
    def get_ip(self, request):
        return helpers.RemoteIPAddress().get_ip_address(request)


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if request.resolver_match.namespace == 'admin':
            return False
        return super().should_check(request)
