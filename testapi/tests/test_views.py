import pytest
from rest_framework.test import APIClient

from django.urls import reverse
from factory import Sequence
from rest_framework import status

from client.tests.factories import ClientFactory
from submission import constants, models
from submission.models import Sender, Submission
from submission.tests.factories import SubmissionFactory, SenderFactory
from client.tests.utils import sign_invalid_client_hawk_header

API_TEST_NAMES_WHITELIST = [
    'delete_test_senders',
    'delete_test_submissions',
    'submissions_by_email',
    'submission',
]


@pytest.fixture
def user():
    return ClientFactory()


def api_client(settings, user, test_api_flag):
    settings.SIGAUTH_URL_NAMES_WHITELIST = API_TEST_NAMES_WHITELIST
    settings.FEATURE_TEST_API_ENABLED = test_api_flag
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_client_test_white_listed(settings):
    settings.SIGAUTH_URL_NAMES_WHITELIST = API_TEST_NAMES_WHITELIST
    settings.FEATURE_TEST_API_ENABLED = True
    client = APIClient()
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

    assert response.status_code == status.HTTP_201_CREATED
    assert models.Submission.objects.count() == 1

    response = api_client_enabled_test_api.get(
        reverse('testapi:submissions_by_email', kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['meta']['recipients'][0] == 'foo@bar.com'
    assert response.json()[0]['is_sent'] is True


@pytest.mark.django_db
def test_return_404_if_no_submissions_are_found(api_client_enabled_test_api):
    assert models.Submission.objects.count() == 0

    response = api_client_enabled_test_api.get(
        reverse('testapi:submissions_by_email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_return_404_if_testapi_is_disabled(api_client_disabled_testapi):
    assert models.Submission.objects.count() == 0

    response = api_client_disabled_testapi.get(
        reverse('testapi:submissions_by_email',
                kwargs={'email_address': 'foo@bar.com'}),
        format='json'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_return_403_when_unauthenticated(api_client_test_white_listed):
    response = api_client_test_white_listed.get(
        reverse('testapi:submissions_by_email',
                kwargs={'email_address': 'foo@bar.com'}),
        HTTP_X_SIGNATURE=sign_invalid_client_hawk_header()
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_test_submissions(api_client_enabled_test_api):
    SubmissionFactory.create_batch(
        3,
        sender=SenderFactory(
            email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
        )
    )
    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Submission.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_submissions_email_action(api_client_enabled_test_api):
    meta = {
        'action_name': constants.ACTION_NAME_EMAIL,
        'recipients': ['test+notification@directory.uktrade.io'],
        'form_url': '/the/form/tests',
        'funnel_steps': ['one', 'two', 'three'],
        'reply_to': 'test@testsubmission.com',
    }
    SubmissionFactory.create_batch(3, meta=meta)

    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Submission.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_submissions_gov_notify_action(
        api_client_enabled_test_api, gov_notify_email_action_payload
):
    email = 'test+govnotifyaction@directory.uktrade.io'
    gov_notify_email_action_payload['meta']['sender']['email_address'] = email
    Submission.objects.create(**gov_notify_email_action_payload)

    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Submission.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_submissions_zendesk_action(
        api_client_enabled_test_api, zendesk_action_payload
):
    email = 'test+zendeskaction@directory.uktrade.io'
    zendesk_action_payload['meta']['email_address'] = email
    Submission.objects.create(**zendesk_action_payload)

    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Submission.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_submissions_returns_404_when_no_test_submissions(
        api_client_enabled_test_api
):
    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_test_submissions_returns_404_with_disabled_testapi(
        api_client_disabled_testapi
):
    SubmissionFactory.create(
        sender=SenderFactory(
            email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
        )
    )
    response = api_client_disabled_testapi.delete(
        reverse('testapi:delete_test_submissions')
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Submission.objects.count() == 1


@pytest.mark.django_db
def test_delete_test_submissions_returns_403_when_unauthenticated(api_client_test_white_listed):
    response = api_client_test_white_listed.delete(
        reverse('testapi:delete_test_submissions'),
        HTTP_X_SIGNATURE=sign_invalid_client_hawk_header(),
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_test_senders(api_client_enabled_test_api):
    SenderFactory.create_batch(
        3,
        email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
    )
    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_senders')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Sender.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_senders_returns_404_when_no_test_senders(api_client_enabled_test_api):
    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_senders')
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_test_senders_returns_404_with_disabled_testapi(api_client_disabled_testapi):
    SenderFactory.create(
        email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
    )
    response = api_client_disabled_testapi.delete(
        reverse('testapi:delete_test_senders')
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Sender.objects.count() == 1


@pytest.mark.django_db
def test_delete_test_senders_returns_403_when_unauthenticated(api_client_test_white_listed):
    response = api_client_test_white_listed.delete(
        reverse('testapi:delete_test_senders'),
        HTTP_X_SIGNATURE=sign_invalid_client_hawk_header(),
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_test_senders_and_submissions(api_client_enabled_test_api):
    SubmissionFactory.create_batch(
        3,
        sender=SenderFactory(
            email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
        )
    )
    response = api_client_enabled_test_api.delete(
        reverse('testapi:delete_test_senders')
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Sender.objects.count() == 0
    assert Submission.objects.count() == 0


@pytest.mark.django_db
def test_delete_test_senders_and_submissions_with_disabled_testapi(api_client_disabled_testapi):
    SubmissionFactory.create_batch(
        3,
        sender=SenderFactory(
            email_address=Sequence(lambda n: f'test+{n}@directory.uktrade.io')
        )
    )
    response = api_client_disabled_testapi.delete(
        reverse('testapi:delete_test_senders')
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Sender.objects.count() == 1
    assert Submission.objects.count() == 3
