import sigauth.middleware
import sigauth.helpers

from django.core.exceptions import ValidationError

from client import models


class RequestSignatureChecker(sigauth.helpers.RequestSignatureChecker):

    MESSAGE_UNKNOWN_SENDER = 'Unknown sender.'
    MESSAGE_INVALID_SENDER = 'Invalid sender.'
    MESSAGE_INACTIVE_SENDER = 'Inactive sender.'

    def lookup_credentials(self, sender_id):
        try:
            queryset = models.Client.objects.all()
            sender = queryset.only('access_key').get(identifier=sender_id)
        except ValidationError:
            raise LookupError(self.MESSAGE_INVALID_SENDER)
        except models.Client.DoesNotExist:
            raise LookupError(self.MESSAGE_UNKNOWN_SENDER)
        else:
            if sender.is_active is False:
                raise LookupError(self.MESSAGE_INACTIVE_SENDER)
            return {
                'id': sender_id,
                'key': sender.access_key,
                'algorithm': self.algorithm
            }


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = None

    def __init__(self, *args, **kwargs):
        self.request_checker = RequestSignatureChecker(self.secret)

    def should_check(self, request):
        if request.resolver_match.namespace == 'admin':
            return False
        return super().should_check(request)
