from rest_framework import serializers


class SubmissionSerializer(serializers.Serializer):

    def to_representation(self, obj):
        return {
            'id': (
                'dit:directory:forms:api:Submission:' + str(obj.id) +
                ':Update'
            ),
            'type': 'Update',
            'created': obj.created.isoformat('T'),
            'object': {
                'type': 'Submission',
                'id': 'dit:directory:forms:api:Submission:' + str(obj.id),
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
            'id': obj.id,
            'email_address': obj.email_address,
            'is_blacklisted': obj.is_blacklisted,
            'is_whitelisted': obj.is_whitelisted,
        }


class ClientSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'name': obj.name,
            'is_active': obj.is_active,
        }
