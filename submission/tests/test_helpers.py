import csv
from unittest import mock

import pytest
from freezegun import freeze_time

from submission import helpers
from submission.tests.factories import SubmissionFactory


def test_send_email_with_html(mailoutbox, settings):
    helpers.send_email(
        subject="this thing",
        reply_to=["reply@example.com"],
        recipients=["to@example.com"],
        text_body="Hello",
        html_body="<a>Hello</a>",
    )
    message = mailoutbox[0]

    assert message.subject == "this thing"
    assert message.from_email == settings.DEFAULT_FROM_EMAIL
    assert message.reply_to == ["reply@example.com"]
    assert message.to == ["to@example.com"]
    assert message.body == "Hello"


def test_send_email_without_html(mailoutbox, settings):
    helpers.send_email(
        subject="this thing",
        reply_to=["reply@example.com"],
        recipients=["to@example.com"],
        text_body="Hello",
    )
    message = mailoutbox[0]

    assert message.subject == "this thing"
    assert message.from_email == settings.DEFAULT_FROM_EMAIL
    assert message.reply_to == ["reply@example.com"]
    assert list(message.to) == ["to@example.com"]
    assert message.body == "Hello"


@mock.patch("submission.helpers.ZendeskUser")
def test_zendesk_client_create_user(mock_user):
    client = helpers.ZendeskClient(
        email="test@example.com",
        token="token123",
        subdomain="subdomain123",
        custom_field_id=123,
    )
    with mock.patch.object(client.client.users, "create_or_update") as stub:
        client.get_or_create_user(
            full_name="Jim Example", email_address="test@example.com"
        )
        assert stub.call_count == 1
        assert stub.call_args == mock.call(
            mock_user(name="Jim Example", email="test@example.com")
        )


@pytest.mark.parametrize(
    "parameters",
    [
        [
            "subject123",
            123,
            {"field": "value"},
            "some-service-name",
            None,
            [{"id": 123, "value": "some-service-name"}],
            "Field: value",
        ],
        [
            "subject123",
            123,
            {},
            "some-service-name",
            None,
            [{"id": 123, "value": "some-service-name"}],
            "",
        ],
        [
            "subject123",
            123,
            {
                "field": "value",
                "_custom_fields": [
                    {"id": "11", "value": "v1"},
                    {"id": "22", "value": "v2"},
                ],
            },
            "some-service-name",
            None,
            [
                {"id": 123, "value": "some-service-name"},
                {"id": "11", "value": "v1"},
                {"id": "22", "value": "v2"},
            ],
            "Field: value",
        ],
        [
            "subject123",
            123,
            {"field": "value", "_custom_fields": []},
            "some-service-name",
            None,
            [{"id": 123, "value": "some-service-name"}],
            "Field: value",
        ],
        [
            "subject123",
            123,
            {"field": "value", "_tags": ["t1", "t2"]},
            "some-service-name",
            ["t1", "t2"],
            [{"id": 123, "value": "some-service-name"}],
            "Field: value",
        ],
        [
            "subject123",
            "123",
            {"field": "value", "_tags": []},
            "some-service-name",
            None,
            [{"id": "123", "value": "some-service-name"}],
            "Field: value",
        ],
    ],
)
@mock.patch("submission.helpers.Ticket")
def test_zendesk_client_create_ticket(mock_ticket, parameters, settings):
    (
        subject,
        custom_field_id,
        payload,
        service_name,
        tags,
        custom_fields,
        description,
    ) = parameters
    client = helpers.ZendeskClient(
        email="test@example.com",
        token="token123",
        subdomain="subdomain123",
        custom_field_id=custom_field_id,
    )

    user = mock.Mock()
    client.client = mock.Mock()
    client.create_ticket(
        subject=subject, payload=payload, zendesk_user=user, service_name=service_name
    )

    assert mock_ticket.call_count == 1
    assert mock_ticket.call_args == mock.call(
        subject=subject,
        description=description,
        submitter_id=user.id,
        requester_id=user.id,
        tags=tags,
        custom_fields=custom_fields,
    )
    assert client.client.tickets.create.call_args == mock.call(mock_ticket())


@mock.patch("submission.helpers.ZendeskClient")
def test_create_zendesk_ticket(mock_zendesk_client, settings):
    zendesk_email = "test@example.com"
    zendesk_token = "token123"
    settings.ZENDESK_CREDENTIALS = {
        settings.ZENDESK_SUBDOMAIN_DEFAULT: {
            "token": zendesk_token,
            "email": zendesk_email,
            "custom_field_id": "1234",
        }
    }

    helpers.create_zendesk_ticket(
        subject="subject123",
        full_name="jim example",
        email_address="test@example.com",
        payload={"field": "value"},
        service_name="some-service",
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
    )

    assert mock_zendesk_client.call_count == 1
    assert mock_zendesk_client.call_args == mock.call(
        email=zendesk_email,
        token=zendesk_token,
        subdomain=settings.ZENDESK_SUBDOMAIN_DEFAULT,
        custom_field_id="1234",
    )
    client = mock_zendesk_client()

    assert client.get_or_create_user.call_count == 1
    assert client.get_or_create_user.call_args == mock.call(
        full_name="jim example",
        email_address="test@example.com",
    )

    assert client.get_or_create_user.call_count == 1
    assert client.create_ticket.call_args == mock.call(
        subject="subject123",
        payload={"field": "value"},
        zendesk_user=client.get_or_create_user(),
        service_name="some-service",
    )


@mock.patch("submission.helpers.ZendeskClient")
def test_create_zendesk_ticket_subdomain(mock_zendesk_client, settings):
    zendesk_email = "123@example.com"
    zendesk_token = "123token"
    settings.ZENDESK_CREDENTIALS = {
        "123": {
            "token": zendesk_token,
            "email": zendesk_email,
            "custom_field_id": "1234",
        }
    }

    helpers.create_zendesk_ticket(
        subject="subject123",
        full_name="jim example",
        email_address="test@example.com",
        payload={"field": "value"},
        service_name="some-service",
        subdomain="123",
    )

    assert mock_zendesk_client.call_count == 1
    assert mock_zendesk_client.call_args == mock.call(
        email=zendesk_email,
        token=zendesk_token,
        subdomain="123",
        custom_field_id="1234",
    )


@mock.patch("submission.helpers.ZendeskClient")
def test_create_zendesk_ticket_unsupported_subdomain(mock_zendesk_client, settings):
    settings.ZENDESK_CREDENTIALS = {}

    with pytest.raises(NotImplementedError):
        helpers.create_zendesk_ticket(
            subject="subject123",
            full_name="jim example",
            email_address="test@example.com",
            payload={"field": "value"},
            service_name="some-service",
            subdomain="1",
        )


@mock.patch("submission.helpers.NotificationsAPIClient")
def test_send_gov_notify_email(mock_notify_client, settings):
    settings.GOV_NOTIFY_API_KEY = "123456"

    helpers.send_gov_notify_email(
        email_address="test@example.com",
        template_id="123-456-789",
        personalisation={"title": "Mr"},
        email_reply_to_id="123",
    )
    assert mock_notify_client.call_count == 1
    assert mock_notify_client.call_args == mock.call("123456")

    assert mock_notify_client().send_email_notification.call_count == 1
    assert mock_notify_client().send_email_notification.call_args == mock.call(
        email_address="test@example.com",
        template_id="123-456-789",
        personalisation={"title": "Mr"},
        email_reply_to_id="123",
    )


@mock.patch("submission.helpers.NotificationsAPIClient")
def test_send_gov_notify_letter(mock_notify_client, settings):
    settings.GOV_NOTIFY_LETTER_API_KEY = "letterkey123"

    helpers.send_gov_notify_letter(
        template_id="123-456-789-2222",
        personalisation={
            "address_line_1": "The Occupier",
            "address_line_2": "123 High Street",
            "postcode": "SW14 6BF",
            "name": "John Smith",
        },
    )

    assert mock_notify_client.call_count == 1
    assert mock_notify_client.call_args == mock.call("letterkey123")

    assert mock_notify_client().send_letter_notification.call_count == 1
    assert mock_notify_client().send_letter_notification.call_args == (
        mock.call(
            template_id="123-456-789-2222",
            personalisation={
                "address_line_1": "The Occupier",
                "address_line_2": "123 High Street",
                "postcode": "SW14 6BF",
                "name": "John Smith",
            },
        )
    )


@mock.patch("requests.post")
def test_send_pardor(mock_post):
    helpers.send_pardot(
        pardot_url="http://www.example.com/some/submission/path/",
        payload={"field": "value"},
    )

    assert mock_post.call_count == 1
    assert mock_post.call_args == mock.call(
        "http://www.example.com/some/submission/path/",
        {"field": "value"},
        allow_redirects=False,
    )


class TestGetSenderEmailAddresses:
    @pytest.mark.parametrize(
        "action_payload,expected",
        [
            ("email_action_payload", "email-user@example.com"),
            ("zendesk_action_payload", "zendesk-user@example.com"),
            ("gov_notify_email_action_payload", "erp+testform@jhgk.com"),
            ("pardot_action_payload", None),
        ],
    )
    def test_get_sender_email_addresses(self, action_payload, expected, request):
        assert (
            helpers.get_sender_email_address(
                request.getfixturevalue(action_payload)["meta"]
            )
            == expected
        )

    def test_get_sender_email_address_notify_action(
        self, gov_notify_email_action_payload
    ):
        del gov_notify_email_action_payload["meta"]["sender"]
        email = helpers.get_sender_email_address(
            gov_notify_email_action_payload["meta"]
        )
        assert email == "notify-user@example.com"

    def test_get_sender_gov_notify_bulk_email_action_payload(
        self, gov_notify_bulk_email_action_payload
    ):
        email = helpers.get_sender_email_address(gov_notify_bulk_email_action_payload)
        assert email is None


def test_get_recipient_email_address_notify_action(gov_notify_email_action_payload):
    email = helpers.get_recipient_email_address(gov_notify_email_action_payload["meta"])
    assert email == "notify-user@example.com"


def test_get_recipient_email_address_bulk_notify_action(
    gov_notify_bulk_email_action_payload,
):
    gov_notify_bulk_email_action_payload["email_address"] = "notify-user@example.com"
    email = helpers.get_recipient_email_address(gov_notify_bulk_email_action_payload)
    assert email == "notify-user@example.com"


def test_get_recipient_email_address_zendesk_action(zendesk_action_payload, settings):
    zendesk_action_payload["meta"]["subdomain"] = settings.ZENDESK_SUBDOMAIN_DEFAULT
    email = helpers.get_recipient_email_address(zendesk_action_payload["meta"])
    assert email == f"{settings.ZENDESK_SUBDOMAIN_DEFAULT}:Market Access"


def test_get_recipient_email_address_email_action(email_action_payload):
    email = helpers.get_recipient_email_address(email_action_payload["meta"])
    assert email == "foo@bar.com,foo2@bar.com"


def test_get_recipient_email_address_pardot_action(pardot_action_payload):
    email = helpers.get_recipient_email_address(pardot_action_payload["meta"])
    assert email is None


def test_get_recipient_email_address_letter_action(gov_notify_letter_action_payload):
    email = helpers.get_recipient_email_address(
        gov_notify_letter_action_payload["meta"]
    )
    assert email is None


@pytest.mark.django_db
@mock.patch("submission.helpers.NotificationsAPIClient")
def test_send_buy_from_uk_enquiries_as_csv(mock_notify_client):
    data = {
        "body": "Testing...",
        "sector": "AIRPORTS",
        "source": "Digital - outdoor advertising digital screens",
        "country": "AU",
        "given_name": "Test",
        "family_name": "Testing",
        "country_name": "Australia",
        "phone_number": "0123456789",
        "source_other": "",
        "email_address": "test@testing.com",
        "organisation_name": "23",
        "organisation_size": "11-50",
        "email_contact_consent": False,
        "telephone_contact_consent": False,
    }
    SubmissionFactory(data=data, form_url="/international/trade/contact/")

    # this will generates email.csv
    helpers.send_buy_from_uk_enquiries_as_csv()

    assert mock_notify_client.call_count == 1

    with open("email.csv", "r") as file:

        csv_file = [row for row in csv.reader(file)]

        # the header/contents of the CSV file
        csv_header = csv_file[0]
        csv_content = csv_file[1]

        for key, value in data.items():
            assert key in csv_header
            assert str(value) in csv_content


@pytest.mark.django_db
@mock.patch("submission.helpers.NotificationsAPIClient")
def test_send_buy_from_uk_enquiries_as_csv_with_older_submission(mock_notify_client):
    data = {
        "body": "Testing - SHOULDNT APPEAR IN CSV",
        "sector": "AIRPORTS",
        "source": "Digital - outdoor advertising digital screens",
        "country": "AU",
        "given_name": "Test",
        "family_name": "Testing",
        "country_name": "Australia",
        "phone_number": "0123456789",
        "source_other": "",
        "email_address": "test@testing.com",
        "organisation_name": "23",
        "organisation_size": "11-50",
        "email_contact_consent": False,
        "telephone_contact_consent": False,
    }

    with freeze_time("2020-01-01"):
        SubmissionFactory(
            data=data,
            form_url="/international/trade/contact/",
        )

    # this will generates email.csv
    helpers.send_buy_from_uk_enquiries_as_csv()

    assert mock_notify_client.call_count == 1

    with open("email.csv", "r") as file:

        csv_file = [row for row in csv.reader(file)]
        # the hedaers of the CSV file
        csv_header = csv_file[0]

        for key, value in data.items():
            assert key in csv_header

        with pytest.raises(IndexError):
            csv_file[1]
