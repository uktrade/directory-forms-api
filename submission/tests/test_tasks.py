import pytest
from unittest import mock

from submission import tasks


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


@mock.patch('submission.helpers.create_helpdesk_ticket')
def test_create_helpdesk_ticket(mock_create_helpdesk_ticket):
    kwargs = {
        'subject': 'subject123',
        'full_name': 'jim example',
        'email_address': 'test@example.com',
        'payload': {'field': 'value'},
        'service_name': 'some-service',
    }
    tasks.create_helpdesk_ticket(submission_id=1, **kwargs)

    assert mock_create_helpdesk_ticket.call_count == 1
    assert mock_create_helpdesk_ticket.call_args == mock.call(**kwargs)


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
