from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import PermissionDenied

from submission import serializers, tasks
from submission.constants import BLACKLISTED_REASON_CHOICES
from client.authentication import ClientSenderIdAuthentication
from ratelimit.utils import is_ratelimited


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        rate_limited = is_ratelimited(self.request, group='submission', key='ip', rate='1/h')
        if  rate_limited:
            tasks.execute_for_submission(serializer.instance)
        else:
            if serializer.instance.sender:
                serializer.instance.sender.is_blacklist = True
                serializer.instance.sender.blacklist_reason = BLACKLISTED_REASON_CHOICES[1]
                serializer.instance.sender.save()
            raise PermissionDenied(detail="Rate limit exceeded")
