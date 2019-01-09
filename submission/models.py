from django.contrib.postgres.fields import JSONField
from django.db import models

import core.helpers


class Submission(core.helpers.TimeStampedModel):

    class Meta:
        ordering = ['-created']

    data = JSONField()
    meta = JSONField()
    is_sent = models.BooleanField(default=False)
    form_url = models.TextField(blank=True, null=True)
    client = models.ForeignKey(
        'client.Client',
        related_name='submissions',
        blank=True,
        null=True,
    )
    sender = models.ForeignKey(
        'submission.Sender',
        related_name='submissions',
        blank=True,
        null=True,
    )

    @property
    def action_name(self):
        return self.meta.get('action_name', 'unknown action')

    @property
    def funnel(self):
        return self.meta.get('funnel_steps', [])


class Sender(core.helpers.TimeStampedModel):

    email_address = models.EmailField()
    is_blacklisted = models.BooleanField(default=False)
    is_whitelisted = models.BooleanField(default=False)

    def __str__(self):
        return self.email_address
