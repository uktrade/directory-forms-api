# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-09 09:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0008_submission_sender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sender',
            name='is_blacklisted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sender',
            name='is_whitelisted',
            field=models.BooleanField(default=False),
        ),
    ]
