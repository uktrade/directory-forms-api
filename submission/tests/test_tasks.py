from unittest import mock

from submission import tasks


def test_task_send_email(mailoutbox, settings):
    tasks.send_email(
        subject='this thing',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        text_body='Hello',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == settings.DEFAULT_FROM_EMAIL
    assert message.reply_to == ['reply@example.com']
    assert list(message.to) == ['to@example.com']
    assert message.body == 'Hello'


@mock.patch('submission.helpers.ZendeskClient')
def test_create_zendesk_ticket(mock_zendesk_client, settings):
    settings.ZENDESK_EMAIL = 'test@example.com'
    settings.ZENDESK_TOKEN = 'token123'
    settings.ZENDESK_SUBDOMAIN = 'subdomain123'

    tasks.create_zendesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'},
        service_name='some-service',
    )

    assert mock_zendesk_client.call_count == 1
    assert mock_zendesk_client.call_args == mock.call(
        email=settings.ZENDESK_EMAIL,
        token=settings.ZENDESK_TOKEN,
        subdomain=settings.ZENDESK_SUBDOMAIN
    )
    client = mock_zendesk_client()

    assert client.get_or_create_user.call_count == 1
    assert client.get_or_create_user.call_args == mock.call(
        full_name='jim example', email_address='test@example.com',
    )

    assert client.get_or_create_user.call_count == 1
    assert client.create_ticket.call_args == mock.call(
        subject='subject123',
        payload={'field': 'value'},
        zendesk_user=client.get_or_create_user(),
        service_name='some-service',
    )
