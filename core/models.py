from django.contrib.postgres.fields import JSONField

from core.helpers import TimeStampedModel


class FormSubmission(TimeStampedModel):
    data = JSONField()
    meta = JSONField()
