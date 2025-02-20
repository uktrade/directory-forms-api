# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-08 12:04
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0007_sender"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="sender",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="submission.Sender",
            ),
        ),
    ]
