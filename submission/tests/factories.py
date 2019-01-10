import factory
import factory.fuzzy

from submission import models


class SenderFactory(factory.django.DjangoModelFactory):

    email_address = factory.Sequence(lambda n: f'test+{n}@example.com')
    is_blacklisted = False
    is_whitelisted = False

    class Meta:
        model = models.Sender
