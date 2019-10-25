from rest_framework import serializers

from client.models import Client


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': f'dit:directoryFormsApi:Submission:{obj.id}:Create',
            'type': 'Create',
            'Create': obj.created.isoformat('T'),
            'actor': {
                'type': 'dit:directoryFormsApi:Submission:Sender',
                'dit:directoryFormsApi:Submission:Sender': SenderSerializer(obj.sender).data,
            },

             'object': {
                'type': 'dit:directoryFormsApi:Submission',
                'id': f'dit:directoryFormsApi:Submission:{obj.id}',
                'dit:directoryFormsApi:Submission:Client': ClientSerializer(obj.client).data,
                'dit:directoryFormsApi:Submission:Meta': obj.meta,
                'content': obj.data,
                'published': obj.created,
                'name': obj.form_url,
                'attributedTo': {
                    'type': f'dit:directoryFormsApi:SubmissionAction:{obj.action_name}',
                    'id': f'dit:directoryFormsApi:SubmissionType:{obj.type}'
                },
            },
        }


class SenderSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'id': f'dit:directoryFormsApi:Sender:{obj.id}',
            'dit:emailAddress': obj.email_address,
            'dit:isBlacklisted': obj.is_blacklisted,
            'dit:isWhitelisted': obj.is_whitelisted,
            'dit:blackListedReason': obj.blacklisted_reason,
        }


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['name', 'is_active']
