from django.contrib.postgres.fields import JSONField

import core.helpers


class Submission(core.helpers.TimeStampedModel):
    data = JSONField()
    meta = JSONField()
