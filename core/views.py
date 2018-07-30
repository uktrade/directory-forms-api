from rest_framework.generics import CreateAPIView

from core import serializers


class FormSubmissionCreateAPIView(CreateAPIView):
    serializer_class = serializers.FormSubmissionModelSerializer
