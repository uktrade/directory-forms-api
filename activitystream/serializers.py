from rest_framework import serializers

from client.models import Client


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': f'dit:directoryFormsApi:Submission:{obj.id}:published',
            'type': 'published',
            'created': obj.created.isoformat('T'),
            'object': {
                'type': 'dit:directoryFormsApi:Submission',
                'id': f'dit:directoryFormsApi:Submission:{obj.id}',
                'sender': SenderSerializer(obj.sender).data,
                'client': ClientSerializer(obj.client).data,
                'meta': obj.meta,
                'content': obj.data,
                'created': obj.created,
                'form_url': obj.form_url
            },
        }


class SenderSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'id': f'dit:directoryFormsApi:Sender:{obj.id}',
            'email_address': obj.email_address,
            'is_blacklisted': obj.is_blacklisted,
            'is_whitelisted': obj.is_whitelisted,
            'blacklisted_reason': obj.blacklisted_reason,
        }


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['name', 'is_active']
