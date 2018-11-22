import pytest

from submission import serializers


@pytest.fixture
def email_submission(email_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=email_action_payload
    )

    assert serializer.is_valid()
    return serializer.save()


@pytest.fixture
def zendesk_submission(zendesk_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=zendesk_action_payload
    )

    assert serializer.is_valid()
    return serializer.save()


@pytest.fixture
def gov_notify_submission(gov_notify_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=gov_notify_action_payload
    )

    assert serializer.is_valid()
    return serializer.save()


@pytest.fixture
def pardot_submission(pardot_action_payload):
    serializer = serializers.SubmissionModelSerializer(
        data=pardot_action_payload
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
def test_email_action_serializer_from_submission(email_submission):
    serializer = serializers.EmailActionSerializer.from_submission(
        email_submission
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'subject': email_submission.meta['subject'],
        'reply_to': email_submission.meta['reply_to'],
        'recipients': email_submission.meta['recipients'],
        'text_body': email_submission.data['text_body'],
        'html_body': email_submission.data['html_body'],
    }


@pytest.mark.django_db
def test_zendesk_action_serializer_from_submission(
    zendesk_submission, settings
):
    serializer = serializers.ZendeskActionSerializer.from_submission(
        zendesk_submission
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'subject': zendesk_submission.meta['subject'],
        'full_name': zendesk_submission.meta['full_name'],
        'email_address': zendesk_submission.meta['email_address'],
        'payload': zendesk_submission.data,
        'subdomain': settings.ZENDESK_SUBDOMAIN_DEFAULT,
        'service_name': zendesk_submission.meta['service_name'],
    }


@pytest.mark.django_db
def test_gov_notify_action_serializer_from_submission(gov_notify_submission):
    serializer = serializers.GovNotifySerializer.from_submission(
        gov_notify_submission
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'template_id': gov_notify_submission.meta['template_id'],
        'email_address': gov_notify_submission.meta['email_address'],
        'personalisation': {
            'title': gov_notify_submission.data['title'],
        }
    }


@pytest.mark.django_db
def test_gov_notify_action_serializer_from_submission_reply_email(
    gov_notify_action_payload
):

    data = {**gov_notify_action_payload}
    data['meta']['email_reply_to_id'] = '123'
    serializer = serializers.SubmissionModelSerializer(data=data)

    assert serializer.is_valid()
    gov_notify_submission = serializer.save()

    serializer = serializers.GovNotifySerializer.from_submission(
        gov_notify_submission
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'template_id': gov_notify_submission.meta['template_id'],
        'email_address': gov_notify_submission.meta['email_address'],
        'personalisation': {
            'title': gov_notify_submission.data['title'],
        },
        'email_reply_to_id': '123',
    }
