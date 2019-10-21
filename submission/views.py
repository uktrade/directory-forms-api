from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import PermissionDenied

from django.conf import settings

from submission import serializers, tasks, helpers
from submission.constants import BLACKLISTED_REASON_CHOICES
from client.authentication import ClientSenderIdAuthentication
from ratelimit.utils import is_ratelimited

from django.http.response import HttpResponse


class Ratelimited(PermissionDenied):
    pass


class SubmissionRateLimitMixin:

    def ratelimit_check(self, serializer):
        rate_limited = False

        if hasattr(serializer, 'instance.sender') and serializer.instance.sender.is_blacklisted:
            return

        request = helpers.get_request_with_sender_ip(serializer.instance)
        if request:
            rate_limited = is_ratelimited(
                request, group='submission', key='ip',
                rate=settings.RATELIMIT_RATE, increment=True
            )

        if rate_limited:
            serializer.instance.sender.is_blacklisted = True
            serializer.instance.sender.blacklisted_reason = BLACKLISTED_REASON_CHOICES[1][0]
            serializer.instance.sender.save()
            raise Ratelimited()


class SubmissionCreateAPIView(SubmissionRateLimitMixin, CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        super().ratelimit_check(serializer)
        tasks.execute_for_submission(serializer.instance)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        try:
            response.render()
        except Exception as e:
            return self.exception_handler(e)
        return response

    def exception_handler(self, exc):
        if isinstance(exc, Ratelimited):
            return HttpResponse('Request blocked by ratelimit', status=429)
        return super().handle_exception(exc)
