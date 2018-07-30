import pytest

from django.urls import reverse

from core import models

from rest_framework.test import APIClient


@pytest.mark.django_db
def test_generic_form_submission_submit(settings):
    client = APIClient()

    settings.SIGAUTH_URL_NAMES_WHITELIST = ['generic-submit']

    assert models.FormSubmission.objects.count() == 0

    payload = {
        'data': {'title': 'hello'},
        'meta': {'backend': 'email', 'recipients': ['foo@bar.com']}
    }
    response = client.post(
        reverse('generic-submit'),
        data=payload,
        format='json'
    )

    assert response.status_code == 201
    assert models.FormSubmission.objects.count() == 1

    instance = models.FormSubmission.objects.last()

    assert instance.data == payload['data']
    assert instance.meta == payload['meta']
