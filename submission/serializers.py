import logging

from rest_framework import serializers

from django.conf import settings

from submission import constants, models, tasks


logger = logging.getLogger(__name__)


class ZendeskActionSerializer(serializers.Serializer):
    MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION = (
        'Client is not setup to use zendesk, specify service name in '
        'forms-api admin.'
    )
    MESSAGE_INCOMPATIBLE_USER_TYPE = (
        'Instance of submission.models.Client must be attached to request.'
    )

    subject = serializers.CharField()
    full_name = serializers.CharField()
    email_address = serializers.EmailField()
    payload = serializers.DictField()
    subdomain = serializers.ChoiceField(
        choices=list(settings.ZENDESK_CREDENTIALS.keys()),
        default=settings.ZENDESK_SUBDOMAIN_DEFAULT,
    )

    def __init__(self, context, *args, **kwargs):
        client = context['request'].user
        if not hasattr(client, 'zendesk_service_name'):
            raise TypeError(self.MESSAGE_INCOMPATIBLE_USER_TYPE)
        super().__init__(context=context, *args, **kwargs)

    @classmethod
    def from_submission(cls, submission, context):
        data = {
            **submission.meta,
            'payload': submission.data,
        }
        return cls(data=data, context=context)

    def validate(self, data):
        client = self.context['request'].user
        if not client.zendesk_service_name:
            logger.error(
                self.MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION,
                extra={'client': client.identifier}
            )
            raise serializers.ValidationError(
                self.MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION
            )
        return super().validate(data)

    def send(self):
        return tasks.create_zendesk_ticket(
            **self.validated_data,
            service_name=self.context['request'].user.zendesk_service_name,
        )


class EmailActionSerializer(serializers.Serializer):

    subject = serializers.CharField()
    reply_to = serializers.ListField(child=serializers.EmailField())
    recipients = serializers.ListField(child=serializers.EmailField())
    html_body = serializers.CharField()
    text_body = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission, context):
        data = {**submission.meta, **submission.data}
        return cls(data=data, context=context)

    def send(self):
        return tasks.send_email(**self.validated_data)


class GovNotifySerializer(serializers.Serializer):

    template_id = serializers.CharField()
    email_address = serializers.EmailField()
    personalisation = serializers.DictField()

    @classmethod
    def from_submission(cls, submission, context):
        data = {**submission.meta, 'personalisation': submission.data}
        return cls(data=data, context=context)

    def send(self):
        return tasks.send_gov_notify(**self.validated_data)


class SubmissionModelSerializer(serializers.ModelSerializer):

    serializer_map = {
        constants.ACTION_NAME_EMAIL: EmailActionSerializer,
        constants.ACTION_NAME_ZENDESK: ZendeskActionSerializer,
        constants.ACTION_NAME_GOV_NOTIFY: GovNotifySerializer,
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
