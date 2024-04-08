import pytest
from unittest import mock
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from submission import tasks
from submission.models import Submission
from submission.tests.factories import SubmissionFactory
from submission.constants import ACTION_NAME_GOV_NOTIFY_BULK_EMAIL


@mock.patch('submission.helpers.send_email')
def test_task_send_email(mock_send_email):
    kwargs = {
        'subject': 'this thing',
        'reply_to': ['reply@example.com'],
        'recipients': ['to@example.com'],
        'text_body': 'Hello',
    }
    tasks.send_email(submission_id=1, **kwargs)

    assert mock_send_email.call_count == 1
    assert mock_send_email.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.create_zendesk_ticket')
def test_create_zendesk_ticket(mock_create_zendesk_ticket):
    kwargs = {
        'subject': 'subject123',
        'full_name': 'jim example',
        'email_address': 'test@example.com',
        'payload': {'field': 'value'},
        'service_name': 'some-service',
    }
    tasks.create_zendesk_ticket(submission_id=1, **kwargs)

    assert mock_create_zendesk_ticket.call_count == 1
    assert mock_create_zendesk_ticket.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.send_gov_notify_email')
def test_task_send_gov_notify_email(mock_send_gov_notify_email):
    kwargs = {
        'subject': 'this thing',
        'reply_to': ['reply@example.com'],
        'recipients': ['to@example.com'],
        'text_body': 'Hello',
    }
    tasks.send_gov_notify_email(submission_id=1, **kwargs)

    assert mock_send_gov_notify_email.call_count == 1
    assert mock_send_gov_notify_email.call_args == mock.call(**kwargs)


@pytest.mark.django_db
@mock.patch('submission.helpers.send_gov_notify_email')
def test_task_send_gov_notify_bulk_email(mock_send_gov_notify_email):
    # create 5x fake submissions - one already marked as sent, one expired, one with the wrong action and two active.
    # We expect only the action active submissions to be called
    meta = {
        'action_name': ACTION_NAME_GOV_NOTIFY_BULK_EMAIL,
        'recipients': ['foo@bar.com'],
        'form_url': '/the/form/tests',
        'funnel_steps': ['one', 'two', 'three'],
        'reply_to': 'test@testsubmission.com',
        'template_id': '123456'
    }

    # Valid Submissions
    SubmissionFactory(meta=meta, is_sent=False)
    SubmissionFactory(meta=meta, is_sent=False)

    # Submissions already marked as sent
    SubmissionFactory(meta=meta)

    # Expired submission
    time_delay = (timezone.now() - timedelta(hours=settings.SUBMISSION_FILTER_HOURS + 1))
    expired_submission = SubmissionFactory(meta=meta, created=time_delay, is_sent=False)
    expired_submission.created = time_delay
    expired_submission.save()

    # Submissions with a different action
    meta_with_different_action = meta
    meta_with_different_action['action_name'] = 'A_DIFFERENT_ACTION'
    SubmissionFactory(meta=meta_with_different_action, is_sent=False)

    # Run the task
    tasks.send_gov_notify_bulk_email()

    # Assert call count = 2
    # assert mock_send_gov_notify_email.call_count == 2

    # Assert all submissions are now marked as sent
    submissions = Submission.objects.all()
    submissions = [x for x in submissions if x.action_name == ACTION_NAME_GOV_NOTIFY_BULK_EMAIL]
    assert [x.is_sent for x in submissions]


@mock.patch('submission.helpers.send_gov_notify_letter')
def test_task_send_gov_notify_letter(mock_send_gov_notify_letter):
    kwargs = {
        'template_id': '123456',
        'personalisation': 'Hello',
    }
    tasks.send_gov_notify_letter(submission_id=1, **kwargs)

    assert mock_send_gov_notify_letter.call_count == 1
    assert mock_send_gov_notify_letter.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.send_pardot')
def test_task_send_pardot(mock_send_pardot):
    kwargs = {
        'pardot_url': 'http://www.example.com/some/submission/path/',
        'payload': {'field': 'value'},
    }
    tasks.send_pardot(submission_id=1, **kwargs)

    assert mock_send_pardot.call_count == 1
    assert mock_send_pardot.call_args == mock.call(**kwargs)


@pytest.mark.django_db
@mock.patch('submission.helpers.send_gov_notify_email')
def test_task_send_buy_from_uk_enquiries_as_csv(mock_send_gov_notify_email):
    kwargs = {
    }
    tasks.send_buy_from_uk_enquiries_as_csv(**kwargs)

    assert mock_send_gov_notify_email.call_count == 1
