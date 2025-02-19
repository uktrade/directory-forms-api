from django.core.exceptions import ValidationError
from sigauth.helpers import RequestSignatureChecker

from client import models

MESSAGE_UNKNOWN_SENDER = "Unknown sender"
MESSAGE_INVALID_SENDER = "Invalid sender"
MESSAGE_INACTIVE_SENDER = "Inactive sender"


class RequestSignatureChecker(RequestSignatureChecker):

    def lookup_credentials(self, sender_id):
        client = lookup_client(sender_id)
        return {"id": sender_id, "key": client.access_key, "algorithm": self.algorithm}


def lookup_client(identifier):
    try:
        client = models.Client.objects.all().get(identifier=identifier)
    except ValidationError:
        raise LookupError(MESSAGE_INVALID_SENDER)
    except models.Client.DoesNotExist:
        raise LookupError(MESSAGE_UNKNOWN_SENDER)
    else:
        if client.is_active is False:
            raise LookupError(MESSAGE_INACTIVE_SENDER)
        return client
