from django.core.mail import EmailMultiAlternatives


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
