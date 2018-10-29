from unittest import mock

import pytest

from django.contrib.auth.models import AnonymousUser

from submission import constants, serializers
from client.models import Client


@pytest.fixture
def email_action_payload():
    return {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': ['reply@example.com'],
        }
    }


@pytest.fixture
def zendesk_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_EMAIL,
            'subject': 'Hello',
            'full_name': 'Jim Example',
            'email_address': 'from@example.com',
        }
    }


@pytest.fixture
def gov_notify_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_GOV_NOTIFY,
            'template_id': '213123',
            'email_address': 'from@example.com',
        }
    }


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
def incomplete_user_information_request(rf):
    request = rf.get('/')
    request.user = Client()
    return request


@pytest.fixture
def authenticated_request(rf):
    request = rf.get('/')
    request.user = Client(zendesk_service_name='Great')
    return request


@pytest.fixture
def anonymous_request(rf):
    request = rf.get('/')
    request.user = AnonymousUser()
    return request


def test_form_submission_serializer():
    data = {
        'data': {'title': 'hello'},
        'meta': {'action_name': 'email', 'recipients': ['foo@bar.com']}
    }
    serializer = serializers.SubmissionModelSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.validated_data == data


@pytest.mark.django_db
def test_submissions_serializer_action_mapping(
    email_action_payload, authenticated_request
):
    serializer = serializers.SubmissionModelSerializer(
        data=email_action_payload,
        context={'request': authenticated_request}
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
def test_email_action_serializer_from_submission(
    email_submission, authenticated_request
):
    serializer = serializers.EmailActionSerializer.from_submission(
        email_submission, context={'request': authenticated_request}
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
@mock.patch('submission.helpers.send_email')
def test_email_action_serializer_send(mock_send_email, email_submission):
    serializer = serializers.EmailActionSerializer.from_submission(
        email_submission, context={'request': authenticated_request}
    )

    assert serializer.is_valid()
    serializer.send()

    assert mock_send_email.call_count == 1
    assert mock_send_email.call_args == mock.call(
        subject=email_submission.meta['subject'],
        reply_to=email_submission.meta['reply_to'],
        recipients=email_submission.meta['recipients'],
        text_body=email_submission.data['text_body'],
        html_body=email_submission.data['html_body'],
    )


@pytest.mark.django_db
def test_zendesk_action_serializer_from_submission(
    zendesk_submission, authenticated_request, settings
):
    serializer = serializers.ZendeskActionSerializer.from_submission(
        zendesk_submission,
        context={'request': authenticated_request}
    )
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'subject': zendesk_submission.meta['subject'],
        'full_name': zendesk_submission.meta['full_name'],
        'email_address': zendesk_submission.meta['email_address'],
        'payload': zendesk_submission.data,
        'subdomain': settings.ZENDESK_SUBDOMAIN_DEFAULT,
    }


@pytest.mark.django_db
@mock.patch('submission.helpers.create_zendesk_ticket')
def test_zendesk_action_serializer_send(
    mock_send_email, zendesk_submission, authenticated_request, settings
):
    serializer = serializers.ZendeskActionSerializer.from_submission(
        zendesk_submission,
        context={'request': authenticated_request}
    )

    assert serializer.is_valid()
    serializer.send()

    assert mock_send_email.call_count == 1
    assert mock_send_email.call_args == mock.call(
        subject=zendesk_submission.meta['subject'],
        full_name=zendesk_submission.meta['full_name'],
        email_address=zendesk_submission.meta['email_address'],
        payload=zendesk_submission.data,
        service_name=authenticated_request.user.zendesk_service_name,
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
    )


@pytest.mark.django_db
def test_zendesk_action_serializer_reject_incompatible_user_type(
    zendesk_submission, anonymous_request
):
    with pytest.raises(TypeError):
        serializers.ZendeskActionSerializer.from_submission(
            zendesk_submission,
            context={'request': anonymous_request}
        )

    with pytest.raises(TypeError):
        serializers.ZendeskActionSerializer(
            data={},
            context={'request': anonymous_request}
        )


@pytest.mark.django_db
def test_zendesk_action_serializer_reject_incompatible_user_data(
    zendesk_submission, zendesk_action_payload,
    incomplete_user_information_request, caplog
):
    request = incomplete_user_information_request
    serializer_class = serializers.ZendeskActionSerializer
    serializer_one = serializer_class.from_submission(
        zendesk_submission, context={'request': request}
    )

    serializer_two = serializer_class(
        data={
            **zendesk_action_payload['meta'],
            'payload': zendesk_action_payload['data'],
        },
        context={'request': request}
    )

    for serializer in [serializer_one, serializer_two]:
        assert serializer.is_valid() is False
        assert serializer.errors['non_field_errors'] == (
            [serializer_class.MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION]
        )
        log = caplog.records()[0]
        assert log.levelname == 'ERROR'
        assert log.msg == serializer.MESSAGE_INCOMPLETE_CLIENT_CONFIGURATION
        assert log.client == request.user.identifier


@pytest.mark.django_db
def test_gov_notify_action_serializer_from_submission(
    gov_notify_submission, authenticated_request
):
    serializer = serializers.GovNotifySerializer.from_submission(
        gov_notify_submission, context={'request': authenticated_request}
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
@mock.patch('submission.helpers.send_gov_notify')
def test_gov_notify_action_serializer_send(
    mock_send_gov_notify, gov_notify_submission
):
    serializer = serializers.GovNotifySerializer.from_submission(
        gov_notify_submission, context={'request': authenticated_request}
    )

    assert serializer.is_valid()
    serializer.send()

    assert mock_send_gov_notify.call_count == 1
    assert mock_send_gov_notify.call_args == mock.call(
        template_id=gov_notify_submission.meta['template_id'],
        email_address=gov_notify_submission.meta['email_address'],
        personalisation=gov_notify_submission.data,
    )
