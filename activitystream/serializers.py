from rest_framework import serializers


DIT_NAMESPACE = 'dit:directoryFormsApi'
DIT_SUBMISSION_NAMESPACE = f'{DIT_NAMESPACE}:Submission'


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': f'{DIT_SUBMISSION_NAMESPACE}:{obj.id}:Create',
            'type': 'Create',
            'published': obj.created.isoformat('T'),
            'actor': SenderSerializer(obj.sender).data,
            'object': {
                'type': f'{DIT_SUBMISSION_NAMESPACE}',
                'id': f'{DIT_SUBMISSION_NAMESPACE}:{obj.id}',
                f'{DIT_SUBMISSION_NAMESPACE}:Meta': obj.meta,
                f'{DIT_SUBMISSION_NAMESPACE}:Data': obj.data,
                'published': obj.created.isoformat('T'),
                'url': obj.form_url,
                'attributedTo': {
                    'type': f'{DIT_NAMESPACE}:SubmissionAction:{obj.action_name}',
                    'id': f'{DIT_NAMESPACE}:SubmissionType:{obj.submission_type}'
                },
            },
        }


class SenderSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
                'type': f'{DIT_SUBMISSION_NAMESPACE}:Sender',
                'id': f'{DIT_NAMESPACE}:Sender:{obj.id}',
                'dit:emailAddress': obj.email_address,
                'dit:isBlacklisted': obj.is_blacklisted,
                'dit:isWhitelisted': obj.is_whitelisted,
                'dit:blackListedReason': obj.blacklisted_reason,
            }
