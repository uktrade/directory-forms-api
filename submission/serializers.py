from rest_framework import serializers

from submission import constants, helpers, models


class ZendeskActionSerializer(serializers.Serializer):

    @classmethod
    def from_submission(cls, submission):
        raise NotImplementedError()

    def send(self):
        raise NotImplementedError()


class EmailActionSerializer(serializers.Serializer):

    subject = serializers.CharField()
    from_email = serializers.EmailField()
    reply_to = serializers.ListField(child=serializers.EmailField())
    recipients = serializers.ListField(child=serializers.EmailField())
    html_body = serializers.CharField()
    text_body = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission):
        try:
            data = {
                'subject': submission.meta['subject'],
                'from_email': submission.meta['from_email'],
                'reply_to': submission.meta['reply_to'],
                'recipients': submission.meta['recipients'],
                'text_body': submission.data['text_body'],
                'html_body': submission.data.get('html_body'),
            }
        except KeyError as error:
            raise serializers.ValidationError(str(error))
        else:
            return cls(data=data)

    def send(self):
        helpers.send_email(**self.validated_data)


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
