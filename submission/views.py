from rest_framework.generics import CreateAPIView

from submission import serializers


class SubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.SubmissionModelSerializer
