from rest_framework import serializers


class SubmissionSerializer(serializers.Serializer):

    DIT_NAMESPACE = 'dit:directoryFormsApi'
    DIT_SUBMISSION_NAMESPACE = f'{DIT_NAMESPACE}:Submission'

    def to_representation(self, obj):
        return {
            'id': f'{self.DIT_SUBMISSION_NAMESPACE}:{obj.id}:Create',
            'type': 'Create',
            'published': obj.created.isoformat('T'),
            'actor': {
                'type': f'{self.DIT_SUBMISSION_NAMESPACE}:Sender',
                'id': f'{self.DIT_NAMESPACE}:Sender:{obj.id}',
                'dit:emailAddress': obj.sender.email_address,
                'dit:isBlacklisted': obj.sender.is_blacklisted,
                'dit:isWhitelisted': obj.sender.is_whitelisted,
                'dit:blackListedReason': obj.sender.blacklisted_reason,
            },
            'object': {
                'type': f'{self.DIT_SUBMISSION_NAMESPACE}',
                'id': f'{self.DIT_SUBMISSION_NAMESPACE}:{obj.id}',
                f'{self.DIT_SUBMISSION_NAMESPACE}:Meta': obj.meta,
                f'{self.DIT_SUBMISSION_NAMESPACE}:Data': obj.data,
                'published': obj.created.isoformat('T'),
                'name': obj.form_url,
                'attributedTo': {
                    'type': f'{self.DIT_NAMESPACE}:SubmissionAction:{obj.action_name}',
                    'id': f'{self.DIT_NAMESPACE}:SubmissionType:{obj.submission_type}'
                },
            },
        }
