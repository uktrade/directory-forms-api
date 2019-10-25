from rest_framework import serializers


class SubmissionSerializer(serializers.Serializer):

    DIT_NAMESPACE = 'dit:directoryFormsApi'

    def to_representation(self, obj):
        return {
            'id': f'{self.DIT_NAMESPACE}:Submission:{obj.id}:Create',
            'type': 'Create',
            'published': obj.created.isoformat('T'),
            'actor': {
                'type': f'{self.DIT_NAMESPACE}:Submission:Sender',
                'id': f'{self.DIT_NAMESPACE}:Sender:{obj.id}',
                'dit:emailAddress': obj.sender.email_address,
                'dit:isBlacklisted': obj.sender.is_blacklisted,
                'dit:isWhitelisted': obj.sender.is_whitelisted,
                'dit:blackListedReason': obj.sender.blacklisted_reason,
            },
            'object': {
                'type': f'{self.DIT_NAMESPACE}:Submission',
                'id': f'{self.DIT_NAMESPACE}:Submission:{obj.id}',
                f'{self.DIT_NAMESPACE}:Meta': obj.meta,
                f'{self.DIT_NAMESPACE}:Data': obj.data,
                'published': obj.created.isoformat('T'),
                'name': obj.form_url,
                'attributedTo': {
                    'type': f'{self.DIT_NAMESPACE}:SubmissionAction:{obj.action_name}',
                    'id': f'{self.DIT_NAMESPACE}:SubmissionType:{obj.submission_type}'
                },
            },
        }
