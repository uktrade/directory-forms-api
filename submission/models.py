from django.contrib.postgres.fields import JSONField
from django.db import models

import core.helpers


class Submission(core.helpers.TimeStampedModel):
    data = JSONField()
    meta = JSONField()
    is_sent = models.BooleanField(default=False)

    @property
    def action_name(self):
        return self.meta.get('action_name', 'unknown action')
