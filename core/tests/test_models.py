import pytest

from django.db import IntegrityError

from core.models import APIClient


@pytest.mark.django_db
def test_api_client_client_id_unique():
    instance = APIClient.objects.create()

    with pytest.raises(IntegrityError):
        APIClient.objects.create(client_id=instance.client_id)


@pytest.mark.django_db
def test_api_client_access_key_hashed_on_create():
    instance = APIClient.objects.create(access_key='Hello')

    assert instance.access_key != 'Hello'

    assert instance.check_access_key('Hello') is True


@pytest.mark.django_db
def test_api_client_access_key_not_hashed_on_edit():
    instance = APIClient.objects.create(access_key='Hello')

    assert instance.check_access_key('Hello') is True

    instance.save()

    assert instance.check_access_key('Hello') is True
