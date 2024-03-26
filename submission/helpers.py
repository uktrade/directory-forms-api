import csv
import json
from datetime import timedelta

import ratelimit.utils
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.test.client import RequestFactory
from django.utils import timezone
from django.utils.safestring import mark_safe
from notifications_python_client import NotificationsAPIClient, prepare_upload
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket
from zenpy.lib.api_objects import User as ZendeskUser

from submission import constants, models


def pprint_json(data):
    dumped = json.dumps(data, indent=4, sort_keys=True)
    return mark_safe(f'<pre>{dumped}</pre>')


class ZendeskClient:

    def __init__(self, email, token, subdomain, custom_field_id):
        self.client = Zenpy(
            timeout=5, email=email, token=token, subdomain=subdomain
        )
        self.custom_field_id = custom_field_id

    def get_or_create_user(self, full_name, email_address):
        zendesk_user = ZendeskUser(name=full_name, email=email_address)
        return self.client.users.create_or_update(zendesk_user)

    def create_ticket(self, subject, payload, zendesk_user, service_name):
        sort_fields_alphabetically = payload.get('_sort_fields_alphabetically', True)
        items = sorted(payload.items()) if sort_fields_alphabetically else payload.items()
        description = [
            '{0}: {1}'.format(key.title().replace('_', ' '), value)
            for key, value in items
            if not key.title().startswith('_')
        ]
        ticket = Ticket(
            subject=subject,
            description='\n'.join(description),
            submitter_id=zendesk_user.id,
            requester_id=zendesk_user.id,
            tags=payload.get('_tags') or None,
            custom_fields=[{'id': self.custom_field_id, 'value': service_name}]
            + (payload.get('_custom_fields') or []),
        )
        return self.client.tickets.create(ticket)


def create_zendesk_ticket(
    subject, full_name, email_address, payload, service_name, subdomain
):
    try:
        credentials = settings.ZENDESK_CREDENTIALS[subdomain]
    except KeyError:
        raise NotImplementedError(f'subdomain {subdomain} not supported')

    client = ZendeskClient(
        email=credentials['email'],
        token=credentials['token'],
        subdomain=subdomain,
        custom_field_id=credentials['custom_field_id'],
    )

    zendesk_user = client.get_or_create_user(
        full_name=full_name, email_address=email_address
    )
    return client.create_ticket(
        subject=subject,
        payload=payload,
        zendesk_user=zendesk_user,
        service_name=service_name,
    )


def send_email(subject, reply_to, recipients, text_body, html_body=None):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        reply_to=reply_to,
        to=recipients,
    )
    if html_body:
        message.attach_alternative(html_body, "text/html")
    message.send()


def send_gov_notify_email(
    template_id, email_address, personalisation, email_reply_to_id=None
):
    client = NotificationsAPIClient(
        settings.GOV_NOTIFY_API_KEY,
    )
    client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
        email_reply_to_id=email_reply_to_id,
    )


def send_gov_notify_letter(template_id, personalisation):
    # Use of separate key so we can use test keys for dev environments.
    # Test keys allow previewing in PDF and not send the letter
    client = NotificationsAPIClient(
        settings.GOV_NOTIFY_LETTER_API_KEY,
    )
    client.send_letter_notification(
        template_id=template_id,
        personalisation=personalisation,
    )


def send_pardot(pardot_url, payload):
    return requests.post(
        pardot_url,
        payload,
        allow_redirects=False,
    )


def get_sender_email_address(submission_meta):
    if submission_meta.get('sender'):
        return submission_meta['sender']['email_address']
    action_name = submission_meta['action_name']
    if action_name == constants.ACTION_NAME_ZENDESK:
        return submission_meta['email_address']
    elif action_name == constants.ACTION_NAME_EMAIL:
        return submission_meta['reply_to'][0]
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_EMAIL:
        return submission_meta['email_address']
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_BULK_EMAIL:
        return None
    elif action_name == constants.ACTION_NAME_PARDOT:
        return None
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_LETTER:
        return None


def get_recipient_email_address(submission_meta):
    action_name = submission_meta['action_name']
    if action_name == constants.ACTION_NAME_ZENDESK:
        sub_domain = submission_meta.get('subdomain')
        service_name = submission_meta.get('service_name')
        return f'{sub_domain}:{service_name}'
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_EMAIL:
        return submission_meta['email_address']
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_BULK_EMAIL:
        return submission_meta['email_address']
    elif action_name == constants.ACTION_NAME_EMAIL:
        return ','.join(submission_meta['recipients'])
    elif action_name == constants.ACTION_NAME_PARDOT:
        return None
    elif action_name == constants.ACTION_NAME_GOV_NOTIFY_LETTER:
        return None


def is_ratelimited(ip_address):
    # Not every action may have an IP address also if the client isn't setting the IP address
    # we need to let the request through to maintain backward compatibility
    if not ip_address:
        return False
    request = RequestFactory().get('/', REMOTE_ADDR=ip_address)
    return ratelimit.utils.is_ratelimited(
        request=request, group='submission', key='ip', rate=settings.RATELIMIT_RATE, increment=True
    )


def send_buy_from_uk_enquiries_as_csv(form_url='/international/trade/contact/'):
    """A method to create last seven days data for buy from uk contact details"""
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    submissions = models.Submission.objects.filter(
        created__gte=week_ago,
        form_url=form_url
    )

    with open('email.csv', 'w+') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow([
            'Sender',
            'body',
            'sector',
            'source',
            'country',
            'given_name',
            'family_name',
            'country_name',
            'phone_number',
            'source_other',
            'email_address',
            'organisation_name',
            'organisation_size',
            'email_contact_consent',
            'telephone_contact_consent',
            'Form',
            'Created'
        ])

        for submission in submissions:
            filewriter.writerow([
                submission.sender,
                submission.data['body'],
                submission.data['sector'],
                submission.data['source'],
                submission.data['country'],
                submission.data['given_name'],
                submission.data['family_name'],
                submission.data['country_name'],
                submission.data['phone_number'],
                submission.data['source_other'],
                submission.data['email_address'],
                submission.data['organisation_name'],
                submission.data['organisation_size'],
                submission.data['email_contact_consent'],
                submission.data['telephone_contact_consent'],
                submission.form_url,
                submission.created,
            ])

    with open('email.csv', 'rb') as f:

        send_gov_notify_email(
            template_id=settings.BUY_FROM_UK_ENQUIRY_TEMPLATE_ID,
            email_address=settings.BUY_FROM_UK_EMAIL_ADDRESS,
            personalisation={'link_to_file': prepare_upload(f, is_csv=True)},
            email_reply_to_id=settings.BUY_FROM_UK_REPLY_TO_EMAIL_ADDRESS
        )
