from rest_framework import serializers

from submission import constants, helpers, models


class ZendeskActionSerializer(serializers.Serializer):
    MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION = (
        'Client is not setup to use zendesk, specify service name in '
        'forms-api admin.'
    )

    subject = serializers.CharField()
    full_name = serializers.CharField()
    email_address = serializers.EmailField()
    payload = serializers.DictField()

    @classmethod
    def from_submission(cls, submission, context=None):
        data = {
            **submission.meta,
            'payload': submission.data,
        }
        return cls(data=data, context=context)

    def send(self):
        return helpers.create_zendesk_ticket(**self.validated_data)

    def validate(self, data):
        if not self.context['request'].user.zendesk_service_name:
            raise serializers.ValidationError(
                self.MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION
            )
        return super().validate(data)


class EmailActionSerializer(serializers.Serializer):

    subject = serializers.CharField()
    reply_to = serializers.ListField(child=serializers.EmailField())
    recipients = serializers.ListField(child=serializers.EmailField())
    html_body = serializers.CharField()
    text_body = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission, context=None):
        data = {**submission.meta, **submission.data}
        return cls(data=data, context=context)

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
        return self.action_serializer_class.from_submission(
            self.instance,
            context=self.context,
        )
