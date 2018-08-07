from unittest import mock

from submission import helpers


def test_send_email_with_html(mailoutbox):
    helpers.send_email(
        subject='this thing',
        from_email='from@example.com',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        text_body='Hello',
        html_body='<a>Hello</a>',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == 'from@example.com'
    assert message.reply_to == ['reply@example.com']
    assert message.to == ['to@example.com']
    assert message.body == 'Hello'


def test_send_email_without_html(mailoutbox):
    helpers.send_email(
        subject='this thing',
        from_email='from@example.com',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        text_body='Hello',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == 'from@example.com'
    assert message.reply_to == ['reply@example.com']
    assert list(message.to) == ['to@example.com']
    assert message.body == 'Hello'


@mock.patch('submission.helpers.ZendeskUser')
def test_zendesk_client_create_user(mock_user):
    client = helpers.ZendeskClient(
        email='test@example.com',
        token='token123',
        subdomain='subdomain123'
    )
    with mock.patch.object(client.client.users, 'create_or_update') as stub:
        client.get_or_create_user(
            full_name='Jim Example',
            email_address='test@example.com'
        )
        assert stub.call_count == 1
        assert stub.call_args == mock.call(
            mock_user(name='Jim Example', email='test@example.com')
        )


@mock.patch('submission.helpers.Ticket')
def test_zendesk_client_create_ticket(mock_ticket):
    client = helpers.ZendeskClient(
        email='test@example.com',
        token='token123',
        subdomain='subdomain123'
    )

    user = mock.Mock()
    with mock.patch.object(client.client.tickets, 'create') as stub:
        client.create_ticket(
            subject='subject123',
            payload={'field': 'value'},
            zendesk_user=user,
        )
        assert stub.call_count == 1
        assert stub.call_args == mock.call(
            mock_ticket(
                subject='subject123',
                description='field: value',
                submitter_id=user.id,
                requester_id=user.id,
            )
        )


@mock.patch('submission.helpers.ZendeskClient')
def test_create_zendesk_ticket(mock_zendesk_client, settings):
    settings.ZENDESK_EMAIL = 'test@example.com'
    settings.ZENDESK_TOKEN = 'token123'
    settings.ZENDESK_SUBDOMAIN = 'subdomain123'

    helpers.create_zendesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'}
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
    )
