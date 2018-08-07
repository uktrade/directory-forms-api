from django.core.mail import EmailMultiAlternatives


from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User as ZendeskUser


class ZendeskClient:

    def __init__(self, email, token, subdomain):
        self.zenpy_client = Zenpy(
            timeout=5, email=email, token=token, subdomain=subdomain
        )

    def get_or_create_user(full_name, email_address):
        zendesk_user = ZendeskUser(name=full_name, email=email_address)
        return zenpy_client.users.create_or_update(zendesk_user)

    def create_ticket(subject, data, zendesk_user):
        description = [
            '{0}: {1}'.format(key.title().replace('_', ' '), value)
            for key, value in sorted(data.items())
        ]
        ticket = Ticket(
            subject=subject,
            description='\n'.join(description),
            submitter_id=zendesk_user.id,
            requester_id=zendesk_user.id,
        )
        return zenpy_client.tickets.create(ticket)


def create_zendesk_ticket(subject, full_name, email_address, payload):
    client = ZendeskClient(
        email = settings.ZENDESK_EMAIL,
        token = settings.ZENDESK_TOKEN,
        subdomain = settings.ZENDESK_SUBDOMAIN
    )
    zendesk_user = client.get_or_create_user(
        full_name=full_name, email_address=email_address
    )
    return client.create_ticket(
        subject=subject,
        data=data,
        zendesk_user=zendesk_user,
    )


def send_email(
    subject, from_email, reply_to, recipients, body_text, body_html=None
):
    message = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=from_email,
        reply_to=reply_to,
        to=recipients,
    )
    if body_html:
        message.attach_alternative(body_html, "text/html")
    message.send()
