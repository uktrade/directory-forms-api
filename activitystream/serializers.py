from rest_framework import serializers


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': f'dit:directoryFormsApi:Submission:{obj.id}:Create',
            'type': 'Create',
            'published': obj.created.isoformat('T'),
            'actor': {
                'type': 'dit:directoryFormsApi:Submission:Sender',
                'id': f'dit:directoryFormsApi:Sender:{obj.id}',
                'dit:emailAddress': obj.sender.email_address,
                'dit:isBlacklisted': obj.sender.is_blacklisted,
                'dit:isWhitelisted': obj.sender.is_whitelisted,
                'dit:blackListedReason': obj.sender.blacklisted_reason,
            },
            'object': {
                'type': 'dit:directoryFormsApi:Submission',
                'id': f'dit:directoryFormsApi:Submission:{obj.id}',
                'dit:directoryFormsApi:Submission:Meta': obj.meta,
                'dit:directoryFormsApi:Submission:Data': obj.data,
                'published': obj.created.isoformat('T'),
                'name': obj.form_url,
                'attributedTo': {
                    'type': f'dit:directoryFormsApi:SubmissionAction:{obj.action_name}',
                    'id': f'dit:directoryFormsApi:SubmissionType:{obj.submission_type}'
                },
            },
        }
