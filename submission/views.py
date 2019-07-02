from rest_framework.generics import CreateAPIView

from submission import serializers, tasks

from client.authentication import ClientSenderIdAuthentication


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        tasks.execute_for_submission(serializer.instance)
