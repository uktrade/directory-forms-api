import factory
import factory.fuzzy

from submission import models


class SenderFactory(factory.django.DjangoModelFactory):

    email_address = factory.Sequence(lambda n: f'test+{n}@example.com')

    class Meta:
        model = models.Sender
