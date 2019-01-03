import csv

from django.conf import settings
from django.db import models
from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField,
)
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _


def generate_csv_response(queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{filename}"'.format(
            filename=filename
        )
    )
    generate_csv(
        file_object=response,
        queryset=queryset,
        excluded_fields=excluded_fields
    )
    return response


def generate_csv(file_object, queryset, excluded_fields):
    model = queryset.model
    fieldnames = sorted(
        [field.name for field in model._meta.get_fields()
         if field.name not in excluded_fields]
    )

    objects = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(objects)

    return writer


class TimeStampedModel(models.Model):
    """Modified version of django_extensions.db.models.TimeStampedModel

    Unfortunately, because null=True needed to be added to create and
    modified fields, inheritance causes issues with field clash.

    """
    created = CreationDateTimeField(_('created'), null=True)
    modified = ModificationDateTimeField(_('modified'), null=True)

    def save(self, **kwargs):
        self.update_modified = kwargs.pop(
            'update_modified', getattr(self, 'update_modified', True))
        super(TimeStampedModel, self).save(**kwargs)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True
