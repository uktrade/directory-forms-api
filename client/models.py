from functools import partial
import uuid

from django_cryptography.fields import encrypt

from django.db import models
from django.utils.crypto import get_random_string

from client import constants
import core.helpers


class Client(core.helpers.TimeStampedModel):
    identifier = models.UUIDField(
        max_length=150,
        unique=True,
        default=uuid.uuid4,
        primary_key=True,
    )
    access_key = encrypt(models.CharField(
        max_length=128,
        default=partial(get_random_string, length=64),
    ))
    name = models.CharField(
        help_text='Human friendly name to help identify the record.',
        max_length=150,
        unique=True,
    )
    zendesk_service_name = models.CharField(
        help_text='Optional service to assign zendesk tickets to.',
        max_length=100,
        choices=[(item, item) for item in constants.ZENDESK_SERVICE_NAMES],
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
