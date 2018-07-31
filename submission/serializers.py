from rest_framework import serializers

from submission import models


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Submission
        fields = (
            'data',
            'meta',
        )
