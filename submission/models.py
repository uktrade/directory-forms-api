from django.contrib.postgres.fields import JSONField
from django.db import models

import core.helpers
from submission import constants


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
    def type(self):
        if self.form_url == 'ERP_FORM_URL':
            return 'ExcepionalReviewProcess'
        else:
            return 'GeneralSubmission'

    @property
    def funnel(self):
        return self.meta.get('funnel_steps', [])

    @property
    def ip_address(self):
        sender = self.meta.get('sender')
        if sender:
            return sender.get('ip_address')
        return


class Sender(core.helpers.TimeStampedModel):

    email_address = models.EmailField(unique=True)
    is_blacklisted = models.BooleanField(default=False)
    is_whitelisted = models.BooleanField(default=False)
    blacklisted_reason = models.CharField(
        max_length=15, choices=constants.BLACKLISTED_REASON_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return self.email_address

    @property
    def is_enabled(self):
        return self.is_whitelisted or not self.is_blacklisted

    def blacklist(self, reason):
        self.is_blacklisted = True
        self.blacklisted_reason = reason
        self.save()
