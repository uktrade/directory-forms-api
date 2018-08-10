from rest_framework.generics import CreateAPIView

from submission import serializers

from client.authentication import ClientSenderIdAuthentication


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        # `SubmissionModelSerializer` contains a generic JSON document.
        # `action_serializer` unpacks the generic JSON document to
        # a serializer specific to the action being performed
        action_serializer = serializer.action_serializer
        action_serializer.is_valid(raise_exception=True)
        action_serializer.send()
