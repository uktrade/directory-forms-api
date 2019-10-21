from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import PermissionDenied

from django.conf import settings

from submission import serializers, tasks, helpers
from submission.constants import BLACKLISTED_REASON_CHOICES, RATE_LIMIT_ERROR
from client.authentication import ClientSenderIdAuthentication
from ratelimit.utils import is_ratelimited


class SubmissionRateLimitMixin:

    def ratelimit_check(self, serializer):
        rate_limited = False

        if hasattr(serializer, 'instance.sender.is_blacklisted') and serializer.instance.sender.is_blacklisted:
            return

        request_sender_ip = helpers.get_request_with_sender_ip(serializer.instance)
        if request_sender_ip:
            print(settings.RATELIMIT_RATE)
            rate_limited = is_ratelimited(
                request_sender_ip, group='submission', key='ip',
                rate=settings.RATELIMIT_RATE, increment=True
            )

        if rate_limited:
            serializer.instance.sender.is_blacklisted = True
            serializer.instance.sender.blacklisted_reason = BLACKLISTED_REASON_CHOICES[1][0]
            serializer.instance.sender.save()
            raise PermissionDenied(detail=RATE_LIMIT_ERROR)


class SubmissionCreateAPIView(SubmissionRateLimitMixin, CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        super().ratelimit_check(serializer)
        tasks.execute_for_submission(serializer.instance)
