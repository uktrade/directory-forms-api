from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from zenpy import Zenpy
from zenpy.lib.api_objects import CustomField, Ticket, User as ZendeskUser


class ZendeskClient:

    def __init__(self, email, token, subdomain):
        self.client = Zenpy(
            timeout=5, email=email, token=token, subdomain=subdomain
        )

    def get_or_create_user(self, full_name, email_address):
        zendesk_user = ZendeskUser(name=full_name, email=email_address)
        return self.client.users.create_or_update(zendesk_user)

    def create_ticket(self, subject, payload, zendesk_user, service_name):
        description = [
            '{0}: {1}'.format(key.title().replace('_', ' '), value)
            for key, value in sorted(payload.items())
        ]
        ticket = Ticket(
            subject=subject,
            description='\n'.join(description),
            submitter_id=zendesk_user.id,
            requester_id=zendesk_user.id,
            custom_fields=[
                CustomField(
                    id=settings.ZENDESK_SERVICE_NAME_CUSTOM_FIELD_ID,
                    value=service_name
                )
            ]
        )
        return self.client.tickets.create(ticket)


def create_zendesk_ticket(
    subject, full_name, email_address, payload, service_name
):
    client = ZendeskClient(
        email=settings.ZENDESK_EMAIL,
        token=settings.ZENDESK_TOKEN,
        subdomain=settings.ZENDESK_SUBDOMAIN
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
