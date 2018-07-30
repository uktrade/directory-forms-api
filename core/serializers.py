from rest_framework import serializers

from core import models


class FormSubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FormSubmission
        fields = (
            'data',
            'meta',
        )
