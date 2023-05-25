import csv

from submission.constants import ACTION_NAME_EMAIL

from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.http import HttpResponse
from bs4 import BeautifulSoup
from django.utils.translation import gettext_lazy as _


class DownloadCSVMixin:
    actions = ['download_csv']

    csv_excluded_fields = []

    def download_csv(self, request, queryset):
        return generate_csv_response(
            queryset=queryset,
            filename=self.csv_filename,
            excluded_fields=self.csv_excluded_fields
        )

    download_csv.short_description = (
        "Download CSV report for selected records"
    )


def generate_csv_response(queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
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
    for item in objects:
        if item['meta']['action_name'] == ACTION_NAME_EMAIL:
            if 'html_body' in item['data']:
                soup = BeautifulSoup(item['data']['html_body'], 'html.parser')
                if soup.body:
                    item['data'] = soup.body.text.strip()
                else:
                    item['data'] = soup.text.strip()

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
