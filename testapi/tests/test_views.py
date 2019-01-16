import pytest
from rest_framework.test import APIClient

from django.urls import reverse

from client.tests.factories import ClientFactory
from submission import models


@pytest.fixture
def user():
    return ClientFactory()


def api_client(settings, user, test_api_flag):
    settings.SIGAUTH_URL_NAMES_WHITELIST = [
        'submissions-by-email',
        'submission'
    ]
    settings.FEATURE_TEST_API_ENABLED = test_api_flag
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_enabled_test_api(settings, user):
    return api_client(settings, user, test_api_flag=True)


@pytest.fixture
def api_client_disabled_testapi(settings, user):
    return api_client(settings, user, test_api_flag=False)


@pytest.mark.django_db
def test_find_submissions_by_email(api_client_enabled_test_api):
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
    response = api_client_enabled_test_api.post(
        reverse('api:submission'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.Submission.objects.count() == 1

    response = api_client_enabled_test_api.get(
        reverse('testapi:submissions-by-email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == 200
    assert response.json()[0]['meta']['recipients'][0] == 'foo@bar.com'
    assert response.json()[0]['is_sent'] is True


@pytest.mark.django_db
def test_return_404_if_no_submissions_are_found(api_client_enabled_test_api):
    assert models.Submission.objects.count() == 0

    response = api_client_enabled_test_api.get(
        reverse('testapi:submissions-by-email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_return_404_if_testapi_is_disabled(api_client_disabled_testapi):
    assert models.Submission.objects.count() == 0

    response = api_client_disabled_testapi.get(
        reverse('testapi:submissions-by-email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == 404


def test_return_401_when_unauthenticated():
    client = APIClient()
    response = client.get(
        reverse('testapi:submissions-by-email',
                kwargs={'email_address': 'foo@bar.com'})
    )
    assert response.status_code == 401
