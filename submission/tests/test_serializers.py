from unittest import mock

import pytest

from submission import constants, serializers


@pytest.fixture
def email_action_payload():
    return {
        'data': {
            'body_text': 'hello there',
            'body_html': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'from_email': 'from@example.com',
            'reply_to': ['reply@example.com'],
        }
    }


@pytest.fixture
def email_submission(email_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=email_action_payload
    )

    assert serializer.is_valid()
    return serializer.save()


def test_form_submission_serializer():
    data = {
        'data': {'title': 'hello'},
        'meta': {'action_name': 'email', 'recipients': ['foo@bar.com']}
    }
    serializer = serializers.SubmissionModelSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.validated_data == data


@pytest.mark.django_db
def test_submissions_serializer_action_mapping(email_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=email_action_payload
    )

    assert serializer.is_valid()
    serializer.save()

    assert (
        serializer.action_serializer_class is serializers.EmailActionSerializer
    )
    assert isinstance(
        serializer.action_serializer, serializers.EmailActionSerializer
    )


@pytest.mark.django_db
def test_submissions_serializer_unknown_action():
    serializer = serializers.SubmissionModelSerializer(
        data={'meta': {'action_name': 'unknown'}, 'data': {}}
    )

    assert serializer.is_valid()
    serializer.save()
    with pytest.raises(NotImplementedError):
        serializer.action_serializer_class


@pytest.mark.django_db
def test_email_action_serializer_from_submission(email_submission):
    serializer = serializers.EmailActionSerializer.from_submission(
        email_submission
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'subject': email_submission.meta['subject'],
        'from_email': email_submission.meta['from_email'],
        'reply_to': email_submission.meta['reply_to'],
        'recipients': email_submission.meta['recipients'],
        'body_text': email_submission.data['body_text'],
        'body_html': email_submission.data['body_html'],
    }


@pytest.mark.django_db
@mock.patch('submission.helpers.send_email')
def test_email_action_serializer_send(mock_send_email, email_submission):
    serializer = serializers.EmailActionSerializer.from_submission(
        email_submission
    )

    assert serializer.is_valid()
    serializer.send()

    assert mock_send_email.call_count == 1
    assert mock_send_email.call_args == mock.call(
        subject=email_submission.meta['subject'],
        from_email=email_submission.meta['from_email'],
        reply_to=email_submission.meta['reply_to'],
        recipients=email_submission.meta['recipients'],
        body_text=email_submission.data['body_text'],
        body_html=email_submission.data['body_html'],
    )
