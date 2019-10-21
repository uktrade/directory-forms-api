from unittest import mock

import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from client.tests.factories import ClientFactory
from submission.tests import factories
from submission import models, constants


@pytest.fixture
def user():
    return ClientFactory()


@pytest.fixture
def api_client(settings, user):
    settings.SIGAUTH_URL_NAMES_WHITELIST = ['submission']
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
@mock.patch('submission.tasks.send_email.delay')
def test_generic_form_submission_submit(mock_delay, api_client):
    assert models.Submission.objects.count() == 0

    payload = {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': 'email',
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': ['reply@example.com'],
            'sender_ip_address': '252.252.928.233'
        }
    }
    response = api_client.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    instance = models.Submission.objects.last()

    assert instance.data == payload['data']
    assert instance.meta == payload['meta']


@pytest.mark.django_db
@mock.patch('submission.helpers.send_email')
def test_generic_form_submission_submit_new_sender(mock_delay, api_client):
    assert models.Submission.objects.count() == 0

    email_address = 'test@testsubmission.com'
    payload = {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': 'email',
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': [email_address],
        }
    }
    response = api_client.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    instance = models.Submission.objects.last()

    assert instance.sender.email_address == email_address
    assert instance.is_sent is True
    assert instance.data == payload['data']
    assert instance.meta == payload['meta']


@pytest.mark.django_db
@mock.patch('submission.tasks.send_email.delay')
def test_generic_form_submission_submit_blacklisted(mock_delay, api_client):
    assert models.Submission.objects.count() == 0

    sender = factories.SenderFactory(
        email_address='test@testsubmission.com',
        is_blacklisted=True
    )

    payload = {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': 'email',
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': [sender.email_address],
        }
    }
    response = api_client.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    instance = models.Submission.objects.last()

    assert instance.is_sent is False
    assert instance.data == payload['data']
    assert instance.meta == payload['meta']


@pytest.mark.django_db
@mock.patch('submission.helpers.send_email')
def test_generic_form_submission_submit_whitelisted(mock_send, api_client):
    assert models.Submission.objects.count() == 0

    sender = factories.SenderFactory(
        email_address='test@testsubmission.com',
        is_whitelisted=True
    )

    payload = {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': 'email',
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': [sender.email_address],
            'ip_address': ['192.168.999.1234'],
        }
    }
    response = api_client.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    instance = models.Submission.objects.last()

    assert instance.is_sent is True
    assert instance.data == payload['data']
    assert instance.meta == payload['meta']


@pytest.mark.django_db
@mock.patch('submission.helpers.send_email')
def test_form_submission_blacklisted_whitelisted(mock_delay, api_client):
    assert models.Submission.objects.count() == 0

    sender = factories.SenderFactory(
        email_address='test@testsubmission.com',
        is_blacklisted=True,
        is_whitelisted=True
    )

    payload = {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': 'email',
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': [sender.email_address],
        }
    }
    response = api_client.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    instance = models.Submission.objects.last()

    assert instance.is_sent is True
    assert instance.data == payload['data']
    assert instance.meta == payload['meta']


@pytest.mark.django_db
@mock.patch('submission.tasks.send_email.delay')
def test_email_action(mock_delay, api_client, email_action_payload):
    response = api_client.post(
        reverse('api:submission'),
        data=email_action_payload,
        format='json'
    )

    assert response.status_code == 201
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        subject=email_action_payload['meta']['subject'],
        reply_to=email_action_payload['meta']['reply_to'],
        recipients=email_action_payload['meta']['recipients'],
        text_body=email_action_payload['data']['text_body'],
        html_body=email_action_payload['data']['html_body'],
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.create_zendesk_ticket.delay')
def test_zendesk_action(
    mock_delay, api_client, zendesk_action_payload, settings
):
    response = api_client.post(
        reverse('api:submission'),
        data=zendesk_action_payload,
        format='json'
    )
    expected_payload = {
        **zendesk_action_payload['data'],
        'ingress_url': zendesk_action_payload['meta']['ingress_url'],
    }

    assert response.status_code == 201
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        subject=zendesk_action_payload['meta']['subject'],
        full_name=zendesk_action_payload['meta']['full_name'],
        email_address=zendesk_action_payload['meta']['email_address'],
        payload=expected_payload,
        service_name=zendesk_action_payload['meta']['service_name'],
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify_email.delay')
def test_gov_notify_email_action(
        mock_delay, api_client, gov_notify_email_action_payload
):
    response = api_client.post(
        reverse('api:submission'),
        data=gov_notify_email_action_payload,
        format='json'
    )

    assert response.status_code == 201, response.json()
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        template_id=gov_notify_email_action_payload['meta']['template_id'],
        email_address=gov_notify_email_action_payload['meta']['email_address'],
        personalisation=gov_notify_email_action_payload['data'],
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify_email.delay')
def test_gov_notify_action_old_constant(
        mock_delay, api_client, gov_notify_action_payload_old
):
    # This can be remove when all clients are using the new gov-notify-action
    response = api_client.post(
        reverse('api:submission'),
        data=gov_notify_action_payload_old,
        format='json'
    )

    assert response.status_code == 201, response.json()
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        template_id=gov_notify_action_payload_old['meta']['template_id'],
        email_address=gov_notify_action_payload_old['meta']['email_address'],
        personalisation=gov_notify_action_payload_old['data'],
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify_letter.delay')
def test_gov_notify_letter_action(
        mock_delay, api_client, gov_notify_letter_action_payload
):
    response = api_client.post(
        reverse('api:submission'),
        data=gov_notify_letter_action_payload,
        format='json'
    )

    assert response.status_code == 201, response.json()
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        template_id=gov_notify_letter_action_payload['meta']['template_id'],
        personalisation=gov_notify_letter_action_payload['data'],
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_pardot.delay')
def test_pardot_action(mock_delay, api_client, pardot_action_payload):
    response = api_client.post(
        reverse('api:submission'),
        data=pardot_action_payload,
        format='json'
    )

    assert response.status_code == 201, response.json()
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        pardot_url=pardot_action_payload['meta']['pardot_url'],
        payload=pardot_action_payload['data'],
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify_email.delay')
def test_email_action_rate_limit_not_exceeded(mock_email, api_client, gov_notify_email_action_payload, settings):
    settings.RATELIMIT_RATE = '100000/s'

    for i in range(25):
        response = api_client.post(
            reverse('api:submission'),
            data=gov_notify_email_action_payload,
            format='json'
        )
        assert response.status_code == 201

    submissions = models.Submission.objects.all()

    assert submissions.count() == 25
    non_black_listed_sender = models.Sender.objects.get(email_address='notify-user@example.com')
    assert non_black_listed_sender.is_blacklisted is False
    assert non_black_listed_sender.blacklisted_reason is None


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify_email.delay')
def test_email_action_rate_limit_exceeded(mock_email, api_client, gov_notify_email_action_payload, settings):
    settings.RATELIMIT_RATE = '5/h'
    for i in range(25):
        response = api_client.post(
            reverse('api:submission'),
            data=gov_notify_email_action_payload,
            format='json'
        )
        # if i < 5:
        assert response.status_code == 201
        # else:
            # assert response.status_code == 403
           #  assert response.json()['detail'] == constants.RATE_LIMIT_ERROR

    assert mock_email.call_count == 5
    black_listed_sender = models.Sender.objects.get(email_address='notify-user@example.com')
    assert black_listed_sender.is_blacklisted
    assert black_listed_sender.blacklisted_reason == constants.BLACKLISTED_REASON_CHOICES[1][0]
