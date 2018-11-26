import logging

from rest_framework import serializers

from django.conf import settings

from submission import models


logger = logging.getLogger(__name__)


class ZendeskActionSerializer(serializers.Serializer):
    subject = serializers.CharField()
    full_name = serializers.CharField()
    email_address = serializers.EmailField()
    payload = serializers.DictField()
    service_name = serializers.CharField()
    subdomain = serializers.ChoiceField(
        choices=list(settings.ZENDESK_CREDENTIALS.keys()),
        default=settings.ZENDESK_SUBDOMAIN_DEFAULT,
    )

    @classmethod
    def from_submission(cls, submission):
        data = {**submission.meta, 'payload': submission.data}
        return cls(data=data)


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


class GovNotifySerializer(serializers.Serializer):
    template_id = serializers.CharField()
    email_address = serializers.EmailField()
    personalisation = serializers.DictField()
    email_reply_to_id = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission):
        data = {**submission.meta, 'personalisation': submission.data}
        return cls(data=data)


class PardotSerializer(serializers.Serializer):

    pardot_url = serializers.URLField()
    payload = serializers.DictField()

    @classmethod
    def from_submission(cls, submission):
        data = {**submission.meta, 'payload': submission.data}
        return cls(data=data)


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Submission
        fields = (
            'data',
            'meta',
        )
