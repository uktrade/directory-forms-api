import logging

from django.conf import settings
from rest_framework import serializers

from submission import constants, helpers, models

logger = logging.getLogger(__name__)


class SaveInDatabaseOnlySerializer(serializers.Serializer):

    @classmethod
    def from_submission(cls, submission, *args, **kwargs):
        data = {**submission.meta, **submission.data}
        return cls(data=data, *args, **kwargs)


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
    def from_submission(cls, submission, *args, **kwargs):
        data = {
            **submission.meta,
            "payload": {
                **submission.data,
                "ingress_url": submission.meta.get("ingress_url"),
                "_sort_fields_alphabetically": submission.meta.get(
                    "sort_fields_alphabetically"
                ),
            },
        }
        return cls(data=data, *args, **kwargs)


class EmailActionSerializer(serializers.Serializer):
    subject = serializers.CharField()
    reply_to = serializers.ListField(child=serializers.EmailField())
    recipients = serializers.ListField(child=serializers.EmailField(), required=True)
    html_body = serializers.CharField()
    text_body = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission, *args, **kwargs):
        data = {**submission.meta, **submission.data}
        return cls(data=data, *args, **kwargs)


class GovNotifyEmailSerializer(serializers.Serializer):
    template_id = serializers.CharField()
    email_address = serializers.EmailField()
    personalisation = serializers.DictField()
    email_reply_to_id = serializers.CharField(required=False)

    @classmethod
    def from_submission(cls, submission, *args, **kwargs):
        data = {**submission.meta, "personalisation": submission.data}
        return cls(data=data, *args, **kwargs)


class GovNotifyBulkEmailEntrySerializer(serializers.Serializer):
    """
    Serializer for bulk_email_entries, which is a list of dictionaries submitted to GovNotifyBulkEmailSerializer.
    These dictionaries are free form as the contain email template data that is unique to each gov.uk email template
    all we are checking for is the presence of a recipient email address, which is mandatory.
    """

    email_address = serializers.CharField()


class GovNotifyBulkEmailSerializer(serializers.Serializer):
    """
    This serializer accepts a list of email data 1>n, in order
    to send email to multiple recipients.

    bulk_email_entries contains a list of dicts of personalised email data. it MUST contain an 'email'
    key for each entry in order to pass serialisation.
    """

    template_id = serializers.CharField()
    bulk_email_entries = serializers.ListField(
        child=GovNotifyBulkEmailEntrySerializer()
    )
    email_reply_to_id = serializers.CharField(required=False)


class GovNotifyLetterSerializer(serializers.Serializer):
    template_id = serializers.CharField()
    personalisation = serializers.DictField()

    @classmethod
    def from_submission(cls, submission, *args, **kwargs):
        data = {**submission.meta, "personalisation": submission.data}
        return cls(data=data, *args, **kwargs)


class PardotSerializer(serializers.Serializer):

    pardot_url = serializers.URLField()
    payload = serializers.DictField()

    @classmethod
    def from_submission(cls, submission, *args, **kwargs):
        data = {**submission.meta, "payload": submission.data}
        return cls(data=data, *args, **kwargs)


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Submission
        fields = (
            "data",
            "meta",
            "form_url",
            "sender",
        )
        extra_kwargs = {"sender": {"required": True}}

    def create(self, validated_data):
        sender_email_address = helpers.get_sender_email_address(validated_data["meta"])
        if sender_email_address:
            sender, _ = models.Sender.objects.get_or_create(
                email_address=sender_email_address
            )
            validated_data["sender_id"] = sender.id
        return super().create(validated_data)

    def to_internal_value(self, data):
        data["form_url"] = data["meta"].pop("form_url", "")
        data["client"] = self.context["request"].user
        # This is required for legacy to support old gov-notify action
        # Can be removed when all client are using the new action constant
        if data["meta"]["action_name"] == "gov-notify":
            data["meta"]["action_name"] = constants.ACTION_NAME_GOV_NOTIFY_EMAIL
        return data


class HCSatEntrySerializer(serializers.Serializer):
    id = (serializers.IntegerField(),)
    feedback_submission_date = serializers.CharField()
    url = serializers.CharField()
    user_journey = serializers.CharField(allow_null=True, allow_blank=True)
    satisfaction_rating = serializers.CharField()
    experienced_issues = serializers.ListField(
        child=serializers.CharField(allow_null=True, allow_blank=True), allow_null=True
    )
    other_detail = serializers.CharField(allow_null=True, allow_blank=True)
    service_improvements_feedback = serializers.CharField(
        allow_null=True, allow_blank=True
    )
    likelihood_of_return = serializers.CharField(allow_null=True, allow_blank=True)
    service_name = serializers.CharField(allow_null=True, allow_blank=True)
    service_specific_feedback = serializers.ListField(
        child=serializers.CharField(allow_null=True, allow_blank=True), allow_null=True
    )
    service_specific_feedback_other = serializers.CharField(
        allow_null=True, allow_blank=True
    )


class HCSatSerializer(serializers.Serializer):
    hcsat_feedback_entries = serializers.ListField(child=HCSatEntrySerializer())
