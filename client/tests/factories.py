import factory
import factory.fuzzy

from client import models


class ClientFactory(factory.django.DjangoModelFactory):

    client_name = factory.fuzzy.FuzzyText(length=12)

    class Meta:
        model = models.Client
