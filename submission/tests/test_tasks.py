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
    tasks.send_email(**kwargs)

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
    tasks.create_zendesk_ticket(**kwargs)

    assert mock_create_zendesk_ticket.call_count == 1
    assert mock_create_zendesk_ticket.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.send_gov_notify')
def test_task_send_gov_notify(mock_send_gov_notify):
    kwargs = {
        'subject': 'this thing',
        'reply_to': ['reply@example.com'],
        'recipients': ['to@example.com'],
        'text_body': 'Hello',
    }
    tasks.send_gov_notify(**kwargs)

    assert mock_send_gov_notify.call_count == 1
    assert mock_send_gov_notify.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.send_pardot')
def test_task_send_pardot(mock_send_pardot):
    kwargs = {
        'pardot_url': 'http://www.example.com/some/submission/path/',
        'payload': {'field': 'value'},
    }
    tasks.send_pardot(**kwargs)

    assert mock_send_pardot.call_count == 1
    assert mock_send_pardot.call_args == mock.call(**kwargs)
