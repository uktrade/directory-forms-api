from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from django.conf import settings

from submission import constants, helpers, serializers, tasks
from client.authentication import ClientSenderIdAuthentication


class Ratelimited(Exception):
    pass


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_ratelimit_check(self, submission):
        if helpers.is_ratelimited(submission.ip_address):
            submission.sender.blacklist(reason=constants.IP_RESTRICTED)
            raise Ratelimited

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.perform_ratelimit_check(serializer.instance)
        tasks.execute_for_submission(serializer.instance)

    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return Response(status=429)
        return super().handle_exception(exc)
