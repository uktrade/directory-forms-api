# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-21 08:41
from __future__ import unicode_literals
from django.db import migrations


def update_blacklist_reason(apps, schema_editor):
    Sender = apps.get_model('submission', 'Sender')
    for sender in Sender.objects.filter(is_blacklisted=True):
        sender.blacklisted_reason = 'MA'
        sender.save()


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0013_auto_20191017_1108'),
    ]

    operations = [
        migrations.RunPython(
            update_blacklist_reason, migrations.RunPython.noop
        ),
    ]