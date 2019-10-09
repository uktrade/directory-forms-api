import factory
import factory.fuzzy
from client.tests.factories import ClientFactory
from submission import constants, models


class SenderFactory(factory.django.DjangoModelFactory):

    email_address = factory.Sequence(lambda n: f'test+{n}@example.com')
    is_blacklisted = False
    is_whitelisted = False

    class Meta:
        model = models.Sender


class SubmissionFactory(factory.django.DjangoModelFactory):
    data = {'title': 'hello'}
    meta = {
               'action_name': constants.ACTION_NAME_EMAIL,
               'recipients': ['foo@bar.com'],
               'form_url': '/the/form/tests',
               'funnel_steps': ['one', 'two', 'three'],
               'reply_to': 'test@testsubmission.com',
           }
    client = factory.SubFactory(ClientFactory)
    sender = factory.SubFactory(SenderFactory)

    is_sent = True

    class Meta:
        model = models.Submission
