from django.contrib.postgres.fields import JSONField

import core.helpers


class Submission(core.helpers.TimeStampedModel):
    data = JSONField()
    meta = JSONField()

    @property
    def action_name(self):
        return self.meta.get('action_name', 'unknown action')
