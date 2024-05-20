import uuid
from functools import partial

from django.db import models
from django.utils.crypto import get_random_string
from django_cryptography.fields import encrypt

import core.helpers


class Client(core.helpers.TimeStampedModel):
    identifier = models.UUIDField(
        verbose_name='Sender ID',
        max_length=150,
        unique=True,
        default=uuid.uuid4,
        primary_key=True,
    )
    access_key = encrypt(models.CharField(
        verbose_name='API key',
        max_length=128,
        default=partial(get_random_string, length=64),
    ))
    name = models.CharField(
        help_text='Human friendly name to help identify the record.',
        max_length=150,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)
