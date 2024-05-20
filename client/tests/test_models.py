import pytest
from django.db import IntegrityError

from client import models


@pytest.mark.django_db
def test_api_client_identifier_unique():
    instance = models.Client.objects.create()

    with pytest.raises(IntegrityError):
        models.Client.objects.create(identifier=instance.identifier)
