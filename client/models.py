from functools import partial
import uuid

from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import get_random_string

from core import helpers


class Client(helpers.TimeStampedModel):
    identifier = models.UUIDField(
        max_length=150,
        unique=True,
        default=uuid.uuid4,
        primary_key=True,
    )
    access_key = models.CharField(
        help_text='Value is plain text during create. Hashed on edit.',
        max_length=128,
        default=partial(get_random_string, length=64),
    )
    name = models.CharField(
        help_text='Human friendly name to help identify the record.',
        max_length=150,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    def check_access_key(self, raw_access_key):
        return check_password(raw_access_key, self.access_key)

    def set_access_key(self, access_key):
        self.access_key = make_password(access_key)

    def save(self, *args, **kwargs):
        # `_state` is not "private", in the same way "_meta" is not, they
        # are just prefixed to avoid conflicting with field names. _state is
        # an instance of `ModelState.
        if self._state.adding is True:
            self.set_access_key(self.access_key)
        return super().save(*args, **kwargs)
