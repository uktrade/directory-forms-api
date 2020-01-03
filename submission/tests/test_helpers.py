from unittest import mock

import pytest

from submission import helpers


def test_send_email_with_html(mailoutbox, settings):
    helpers.send_email(
        subject='this thing',
        reply_to=['reply@example.com'],
        recipients=['to@example.com'],
        text_body='Hello',
        html_body='<a>Hello</a>',
    )
    message = mailoutbox[0]

    assert message.subject == 'this thing'
    assert message.from_email == settings.DEFAULT_FROM_EMAIL
    assert message.reply_to == ['reply@example.com']
    assert message.to == ['to@example.com']
    assert message.body == 'Hello'


def test_send_email_without_html(mailoutbox, settings):
    helpers.send_email(
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


@mock.patch('submission.helpers.ZendeskUser')
def test_zendesk_client_create_user(mock_user):
    client = helpers.ZendeskClient(
        email='test@example.com',
        token='token123',
        subdomain='subdomain123',
        custom_field_id=123,
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
@mock.patch('submission.helpers.CustomField')
def test_zendesk_client_create_ticket(
    mock_custom_field, mock_ticket, settings
):
    client = helpers.ZendeskClient(
        email='test@example.com',
        token='token123',
        subdomain='subdomain123',
        custom_field_id=123,
    )

    user = mock.Mock()
    with mock.patch.object(client.client.tickets, 'create') as stub:
        client.create_ticket(
            subject='subject123',
            payload={'field': 'value'},
            zendesk_user=user,
            service_name='some-service'
        )
        assert stub.call_count == 1
        assert stub.call_args == mock.call(
            mock_ticket(
                subject='subject123',
                description='field: value',
                submitter_id=user.id,
                requester_id=user.id,
                custom_fields=[
                    mock_custom_field(
                        id=123,
                        value='some-service',
                    )
                ]
            )
        )


@mock.patch('submission.helpers.ZendeskClient')
def test_create_zendesk_ticket(mock_zendesk_client, settings):
    zendesk_email = 'test@example.com'
    zendesk_token = 'token123'
    settings.ZENDESK_CREDENTIALS = {
        settings.ZENDESK_SUBDOMAIN_DEFAULT: {
            'token': zendesk_token,
            'email': zendesk_email,
            'custom_field_id': '1234',
        }
    }

    helpers.create_zendesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'},
        service_name='some-service',
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
    )

    assert mock_zendesk_client.call_count == 1
    assert mock_zendesk_client.call_args == mock.call(
        email=zendesk_email,
        token=zendesk_token,
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
        custom_field_id='1234',
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


@mock.patch('submission.helpers.ZendeskClient')
def test_create_zendesk_ticket_subdomain(mock_zendesk_client, settings):
    zendesk_email = '123@example.com'
    zendesk_token = '123token'
    settings.ZENDESK_CREDENTIALS = {
        '123': {
            'token': zendesk_token,
            'email': zendesk_email,
            'custom_field_id': '1234',
        }
    }

    helpers.create_zendesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'},
        service_name='some-service',
        subdomain='123',
    )

    assert mock_zendesk_client.call_count == 1
    assert mock_zendesk_client.call_args == mock.call(
        email=zendesk_email,
        token=zendesk_token,
        subdomain='123',
        custom_field_id='1234',
    )


@mock.patch('submission.helpers.ZendeskClient')
def test_create_zendesk_ticket_unsupported_subdomain(
    mock_zendesk_client, settings
):
    settings.ZENDESK_CREDENTIALS = {}

    with pytest.raises(NotImplementedError):
        helpers.create_zendesk_ticket(
            subject='subject123',
            full_name='jim example',
            email_address='test@example.com',
            payload={'field': 'value'},
            service_name='some-service',
            subdomain='1',
        )


@mock.patch('submission.helpers.NotificationsAPIClient')
def test_send_gov_notify_email(mock_notify_client, settings):
    settings.GOV_NOTIFY_API_KEY = '123456'

    helpers.send_gov_notify_email(
        email_address='test@example.com',
        template_id='123-456-789',
        personalisation={'title': 'Mr'},
        email_reply_to_id='123',
    )
    assert mock_notify_client.call_count == 1
    assert mock_notify_client.call_args == mock.call('123456')

    assert mock_notify_client().send_email_notification.call_count == 1
    assert mock_notify_client().send_email_notification.call_args == mock.call(
        email_address='test@example.com',
        template_id='123-456-789',
        personalisation={'title': 'Mr'},
        email_reply_to_id='123',
    )


@mock.patch('submission.helpers.NotificationsAPIClient')
def test_send_gov_notify_letter(mock_notify_client, settings):
    settings.GOV_NOTIFY_LETTER_API_KEY = 'letterkey123'

    helpers.send_gov_notify_letter(
        template_id='123-456-789-2222',
        personalisation={
            'address_line_1': 'The Occupier',
            'address_line_2': '123 High Street',
            'postcode': 'SW14 6BF',
            'name': 'John Smith',
        },
    )

    assert mock_notify_client.call_count == 1
    assert mock_notify_client.call_args == mock.call('letterkey123')

    assert mock_notify_client().send_letter_notification.call_count == 1
    assert mock_notify_client().send_letter_notification.call_args == (
            mock.call(
                template_id='123-456-789-2222',
                personalisation={
                    'address_line_1': 'The Occupier',
                    'address_line_2': '123 High Street',
                    'postcode': 'SW14 6BF',
                    'name': 'John Smith',
                },
            )
    )


@mock.patch('requests.post')
def test_send_pardor(mock_post):
    helpers.send_pardot(
        pardot_url='http://www.example.com/some/submission/path/',
        payload={'field': 'value'},
    )

    assert mock_post.call_count == 1
    assert mock_post.call_args == mock.call(
        'http://www.example.com/some/submission/path/',
        {'field': 'value'},
        allow_redirects=False,
    )


def test_get_sender_email_address_email_action(email_action_payload):
    email = helpers.get_sender_email_address(email_action_payload['meta'])
    assert email == 'email-user@example.com'


def test_get_sender_email_address_zendesk_action(zendesk_action_payload):
    email = helpers.get_sender_email_address(zendesk_action_payload['meta'])
    assert email == 'zendesk-user@example.com'


def test_get_sender_email_address_notify_action(gov_notify_email_action_payload):
    del gov_notify_email_action_payload['meta']['sender']
    email = helpers.get_sender_email_address(gov_notify_email_action_payload['meta'])
    assert email == 'notify-user@example.com'


def test_get_sender_email_address_pardot_action(pardot_action_payload):
    email = helpers.get_sender_email_address(pardot_action_payload['meta'])
    assert email is None


def test_get_sender_email_address_sender(gov_notify_email_action_payload):
    email = helpers.get_sender_email_address(gov_notify_email_action_payload['meta'])
    assert email == 'erp+testform@jhgk.com'


def test_get_recipient_email_address_notify_action(gov_notify_email_action_payload):
    email = helpers.get_recipient_email_address(gov_notify_email_action_payload['meta'])
    assert email == 'notify-user@example.com'


def test_get_recipient_email_address_zendesk_action(zendesk_action_payload):
    email = helpers.get_recipient_email_address(zendesk_action_payload['meta'])
    assert email == 'zendesk-user@example.com'


def test_get_recipient_email_address_email_action(email_action_payload):
    email = helpers.get_recipient_email_address(email_action_payload['meta'])
    assert email == 'foo@bar.com,foo2@bar.com'


def test_get_recipient_email_address_pardot_action(pardot_action_payload):
    email = helpers.get_recipient_email_address(pardot_action_payload['meta'])
    assert email is None


def test_get_recipient_email_address_letter_action(gov_notify_letter_action_payload):
    email = helpers.get_recipient_email_address(gov_notify_letter_action_payload['meta'])
    assert email is None
