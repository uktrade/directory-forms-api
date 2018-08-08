from rest_framework import serializers

from submission import constants, helpers, models


class ZendeskActionSerializer(serializers.Serializer):

    subject = serializers.CharField()
    full_name = serializers.CharField()
    email_address = serializers.EmailField()
    payload = serializers.DictField()

    @classmethod
    def from_submission(cls, submission):
        data = {
            **submission.meta,
            'payload': submission.data,
        }
        return cls(data=data)

    def send(self):
        return helpers.create_zendesk_ticket(**self.validated_data)


class EmailActionSerializer(serializers.Serializer):

    subject = serializers.CharField()
    reply_to = serializers.ListField(child=serializers.EmailField())
    recipients = serializers.ListField(child=serializers.EmailField())
    html_body = serializers.CharField()
    text_body = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission):
        data = {**submission.meta, **submission.data}
        return cls(data=data)

    def send(self):
        return helpers.send_email(**self.validated_data)


class SubmissionModelSerializer(serializers.ModelSerializer):

    serializer_map = {
        constants.ACTION_NAME_EMAIL: EmailActionSerializer,
        constants.ACTION_NAME_ZENDESK: ZendeskActionSerializer,
    }

    class Meta:
        model = models.Submission
        fields = (
            'data',
            'meta',
        )

    @property
    def action_serializer_class(self):
        try:
            return self.serializer_map[self.instance.action_name]
        except KeyError:
            raise NotImplementedError(self.instance.action_name)

    @property
    def action_serializer(self):
        return self.action_serializer_class.from_submission(self.instance)
