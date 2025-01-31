# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-05 23:47
from __future__ import unicode_literals

from urllib.parse import urlparse

from django.db import migrations


def set_form_url(apps, schema_editor):
    Submission = apps.get_model("submission", "Submission")
    for submission in Submission.objects.filter(data__form_url__isnull=False):
        try:
            parsed = urlparse(submission.data["form_url"])
        except AttributeError:
            pass
        else:
            submission.form_url = parsed.path
            submission.save()


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0004_submission_form_url"),
    ]

    operations = [
        migrations.RunPython(set_form_url, migrations.RunPython.noop),
    ]
