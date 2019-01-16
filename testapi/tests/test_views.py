import pytest
from rest_framework.test import APIClient

from django.urls import reverse

from client.tests.factories import ClientFactory
from submission import models


@pytest.fixture
def user():
    return ClientFactory()


@pytest.fixture
def api_client(settings, user):
    settings.SIGAUTH_URL_NAMES_WHITELIST = ['submissions-by-email']
    settings.FEATURE_TEST_API_ENABLED = True
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_find_submissions_by_email(api_client):
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

    response = api_client.get(
        reverse('testapi:submissions-by-email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == 200
