from core import serializers


def test_form_submission_serializer():
    data = {
        'data': {'title': 'hello'},
        'meta': {'backend': 'email', 'recipients': ['foo@bar.com']}
    }
    serializer = serializers.FormSubmissionModelSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.validated_data == data
