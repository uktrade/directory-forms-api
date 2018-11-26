from unittest import mock

import pytest
from rest_framework.test import APIClient

from django.urls import reverse

from submission import models


@pytest.fixture
def api_client(settings):
    settings.SIGAUTH_URL_NAMES_WHITELIST = ['submission']
    return APIClient()


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

    assert response.status_code == 201
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        subject=zendesk_action_payload['meta']['subject'],
        full_name=zendesk_action_payload['meta']['full_name'],
        email_address=zendesk_action_payload['meta']['email_address'],
        payload=zendesk_action_payload['data'],
        service_name=zendesk_action_payload['meta']['service_name'],
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
        submission_id=models.Submission.objects.last().pk,
    )


@pytest.mark.django_db
@mock.patch('submission.tasks.send_gov_notify.delay')
def test_gov_notify_action(mock_delay, api_client, gov_notify_action_payload):
    response = api_client.post(
        reverse('api:submission'),
        data=gov_notify_action_payload,
        format='json'
    )

    assert response.status_code == 201, response.json()
    assert mock_delay.call_count == 1
    assert mock_delay.call_args == mock.call(
        template_id=gov_notify_action_payload['meta']['template_id'],
        email_address=gov_notify_action_payload['meta']['email_address'],
        personalisation=gov_notify_action_payload['data'],
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
