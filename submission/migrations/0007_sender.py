# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-08 11:32
from __future__ import unicode_literals

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0006_auto_20190103_1604"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sender",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, null=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, null=True, verbose_name="modified"
                    ),
                ),
                ("email_address", models.EmailField(max_length=254)),
                ("is_blacklisted", models.BooleanField()),
                ("is_whitelisted", models.BooleanField()),
            ],
            options={
                "ordering": ("-modified", "-created"),
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
    ]
