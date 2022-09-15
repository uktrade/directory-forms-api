import csv
from unittest import mock

import pytest
from freezegun import freeze_time

from submission import helpers
from submission.tests.factories import SubmissionFactory
from helpdesk_client import get_helpdesk_interface


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

@mock.patch(
    'submission.helpers.get_helpdesk_interface',
    return_value=get_helpdesk_interface("helpdesk_client.interfaces.HelpDeskStubbed")
)
def test_create_helpdesk_ticket(mock_client, settings):
    helpdesk_email = 'test@example.com'
    helpdesk_token = 'token123'
    settings.HELP_DESK_INTERFACE = "helpdesk_client.interfaces.HelpDeskStubbed"
    settings.HELP_DESK_CREDENTIALS = {
        'default': {
            'token': helpdesk_token,
            'email': helpdesk_email,
            'custom_field_id': '1234',
            'subdomain': 'default'
        }
    }

    ticket_response = helpers.create_helpdesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'},
        service_name='some-service',
        subdomain='default',
    )

    assert ticket_response.id == 1
    assert ticket_response.subject == "subject123"
    assert ticket_response.description == "Field: value"

@mock.patch(
    'submission.helpers.get_helpdesk_interface',
    return_value=get_helpdesk_interface("helpdesk_client.interfaces.HelpDeskStubbed")
)
def test_create_helpdesk_ticket_subdomain(mock_client, settings):
    helpdesk_email = '123@example.com'
    helpdesk_token = '123token'
    settings.HELP_DESK_INTERFACE = "helpdesk_client.interfaces.HelpDeskStubbed"
    settings.HELP_DESK_CREDENTIALS = {
        'default': {
            'token': helpdesk_token,
            'email': helpdesk_email,
            'custom_field_id': '1234',
            'subdomain': 'default'
        }
    }

    ticket_response = helpers.create_helpdesk_ticket(
        subject='subject123',
        full_name='jim example',
        email_address='test@example.com',
        payload={'field': 'value'},
        service_name='some-service',
        subdomain='default',
    )

    assert ticket_response.id == 1
    assert ticket_response.subject == "subject123"
    assert ticket_response.description == "Field: value"

@mock.patch(
    'submission.helpers.get_helpdesk_interface',
    return_value=get_helpdesk_interface("helpdesk_client.interfaces.HelpDeskStubbed")
)
def test_create_helpdesk_ticket_unsupported_subdomain(mock_client, settings):
    settings.HELP_DESK_CREDENTIALS = {}

    with pytest.raises(NotImplementedError):
        helpers.create_helpdesk_ticket(
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


def test_get_sender_email_address_helpdesk_action(helpdesk_action_payload):
    email = helpers.get_sender_email_address(helpdesk_action_payload['meta'])
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


def test_get_recipient_email_address_helpdesk_action(helpdesk_action_payload, settings):
    helpdesk_action_payload['meta']['subdomain'] = settings.HELP_DESK_SUBDOMAIN_DEFAULT
    email = helpers.get_recipient_email_address(helpdesk_action_payload['meta'])
    assert email == f'{settings.HELP_DESK_SUBDOMAIN_DEFAULT}:Market Access'


def test_get_recipient_email_address_email_action(email_action_payload):
    email = helpers.get_recipient_email_address(email_action_payload['meta'])
    assert email == 'foo@bar.com,foo2@bar.com'


def test_get_recipient_email_address_pardot_action(pardot_action_payload):
    email = helpers.get_recipient_email_address(pardot_action_payload['meta'])
    assert email is None


def test_get_recipient_email_address_letter_action(gov_notify_letter_action_payload):
    email = helpers.get_recipient_email_address(
        gov_notify_letter_action_payload['meta']
    )
    assert email is None


@pytest.mark.django_db
@mock.patch('submission.helpers.NotificationsAPIClient')
def test_send_buy_from_uk_enquiries_as_csv(mock_notify_client):
    data = {
        'body': 'Testing...',
        'sector': 'AIRPORTS',
        'source': 'Digital - outdoor advertising digital screens',
        'country': 'AU',
        'given_name': 'Test',
        'family_name': 'Testing',
        'country_name': 'Australia',
        'phone_number': '0123456789',
        'source_other': '',
        'email_address': 'test@testing.com',
        'organisation_name': '23',
        'organisation_size': '11-50',
        'email_contact_consent': False,
        'telephone_contact_consent': False
    }
    SubmissionFactory(
        data=data,
        form_url='/international/trade/contact/'
    )

    # this will generates email.csv
    helpers.send_buy_from_uk_enquiries_as_csv()

    assert mock_notify_client.call_count == 1

    with open('email.csv', 'r') as file:

        csv_file = [row for row in csv.reader(file)]

        # the header/contents of the CSV file
        csv_header = csv_file[0]
        csv_content = csv_file[1]

        for key, value in data.items():
            assert key in csv_header
            assert str(value) in csv_content


@pytest.mark.django_db
@mock.patch('submission.helpers.NotificationsAPIClient')
def test_send_buy_from_uk_enquiries_as_csv_with_older_submission(mock_notify_client):
    data = {
        'body': 'Testing - SHOULDNT APPEAR IN CSV',
        'sector': 'AIRPORTS',
        'source': 'Digital - outdoor advertising digital screens',
        'country': 'AU',
        'given_name': 'Test',
        'family_name': 'Testing',
        'country_name': 'Australia',
        'phone_number': '0123456789',
        'source_other': '',
        'email_address': 'test@testing.com',
        'organisation_name': '23',
        'organisation_size': '11-50',
        'email_contact_consent': False,
        'telephone_contact_consent': False
    }

    with freeze_time("2020-01-01"):
        SubmissionFactory(
            data=data,
            form_url='/international/trade/contact/',
        )

    # this will generates email.csv
    helpers.send_buy_from_uk_enquiries_as_csv()

    assert mock_notify_client.call_count == 1

    with open('email.csv', 'r') as file:

        csv_file = [row for row in csv.reader(file)]
        # the hedaers of the CSV file
        csv_header = csv_file[0]

        for key, value in data.items():
            assert key in csv_header

        with pytest.raises(IndexError):
            csv_file[1]
