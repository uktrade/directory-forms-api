from unittest import mock

from submission import tasks


@mock.patch('submission.helpers.send_email')
def test_task_send_email(mock_send_enail, settings):
    kwargs = {
        'subject': 'this thing',
        'reply_to': ['reply@example.com'],
        'recipients': ['to@example.com'],
        'text_body': 'Hello',
    }
    tasks.send_email(**kwargs)

    assert mock_send_enail.call_count == 1
    assert mock_send_enail.call_args == mock.call(**kwargs)


@mock.patch('submission.helpers.create_zendesk_ticket')
def test_create_zendesk_ticket(mock_create_zendesk_ticket, settings):
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
def test_task_send_gov_notify(mock_send_gov_notify, settings):
    kwargs = {
        'subject': 'this thing',
        'reply_to': ['reply@example.com'],
        'recipients': ['to@example.com'],
        'text_body': 'Hello',
    }
    tasks.send_gov_notify(**kwargs)

    assert mock_send_gov_notify.call_count == 1
    assert mock_send_gov_notify.call_args == mock.call(**kwargs)
