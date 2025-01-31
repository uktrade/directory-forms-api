from rest_framework import serializers

DIT_NAMESPACE = "dit:directoryFormsApi"
DIT_SUBMISSION_NAMESPACE = f"{DIT_NAMESPACE}:Submission"


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            "id": f"{DIT_SUBMISSION_NAMESPACE}:{obj.id}:Create",
            "type": "Create",
            "published": obj.created.isoformat("T"),
            "actor": SenderSerializer(obj.sender).data,
            "object": {
                "type": f"{DIT_SUBMISSION_NAMESPACE}",
                "id": f"{DIT_SUBMISSION_NAMESPACE}:{obj.id}",
                f"{DIT_SUBMISSION_NAMESPACE}:Meta": obj.meta,
                f"{DIT_SUBMISSION_NAMESPACE}:Data": obj.data,
                "published": obj.created.isoformat("T"),
                "url": obj.form_url,
                "attributedTo": {
                    "type": f"{DIT_NAMESPACE}:SubmissionAction:{obj.action_name}",
                    "id": f"{DIT_NAMESPACE}:SubmissionType:{obj.submission_type}",
                },
            },
        }


class SenderSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            "type": f"{DIT_SUBMISSION_NAMESPACE}:Sender",
            "id": f"{DIT_NAMESPACE}:Sender:{obj.id}",
            "dit:emailAddress": obj.email_address,
            "dit:isBlacklisted": obj.is_blacklisted,
            "dit:isWhitelisted": obj.is_whitelisted,
            "dit:blackListedReason": obj.blacklisted_reason,
        }


class ActivityStreamDomesticHCSATUserFeedbackDataSerializer(
    serializers.ModelSerializer
):
    """
    Domestic HCSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source="created")  # noqa: N815
    url = serializers.CharField(source="URL")  # noqa: N815

    # class Meta:
    #     model = SubmissionSerializer
    #     fields = [
    #         'id',
    #         'feedback_submission_date',
    #         'url',
    #         'user_journey',
    #         'satisfaction_rating',
    #         'experienced_issues',
    #         'other_detail',
    #         'service_improvements_feedback',
    #         'likelihood_of_return',
    #         'service_name',
    #         'service_specific_feedback',
    #         'service_specific_feedback_other',
    #     ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = "dit:domestic:HCSATFeedbackData"
        type = "Update"

        return {
            "id": f"{prefix}:{instance.id}:{type}",
            "type": f"{type}",
            "object": {
                "id": f"{prefix}:{instance.id}",
                "type": prefix,
                **{f"{k}": v for k, v in super().to_representation(instance).items()},
            },
        }
