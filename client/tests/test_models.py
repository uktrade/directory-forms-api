import pytest

from django.db import IntegrityError

from client import models


@pytest.mark.django_db
def test_api_client_client_id_unique():
    instance = models.Client.objects.create()

    with pytest.raises(IntegrityError):
        models.Client.objects.create(client_id=instance.client_id)


@pytest.mark.django_db
def test_api_client_access_key_hashed_on_create():
    instance = models.Client.objects.create(access_key='Hello')

    assert instance.access_key != 'Hello'

    assert instance.check_access_key('Hello') is True


@pytest.mark.django_db
def test_api_client_access_key_not_hashed_on_edit():
    instance = models.Client.objects.create(access_key='Hello')

    assert instance.check_access_key('Hello') is True

    instance.save()

    assert instance.check_access_key('Hello') is True
