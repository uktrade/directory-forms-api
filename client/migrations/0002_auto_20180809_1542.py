# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-09 15:42
from __future__ import unicode_literals

import functools

import django.utils.crypto
import django_cryptography.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="zendesk_service_name",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Auth broker", "Auth broker"),
                    ("Data Hub CRM", "Data Hub CRM"),
                    ("Data Hub MI", "Data Hub MI"),
                    ("Data Hub OMIS", "Data Hub OMIS"),
                    ("Data Protection", "Data Protection"),
                    ("Datahub", "Datahub"),
                    ("Digital Workspace", "Digital Workspace"),
                    ("Directory", "Directory"),
                    ("E-Exporting S00 Triage   ", "E-Exporting S00 Triage   "),
                    ("EIG", "EIG"),
                    ("Export Ops", "Export Ops"),
                    ("Export Vouchers", "Export Vouchers"),
                    ("Find a Supplier", "Find a Supplier"),
                    ("Great", "Great"),
                    ("Invest in GB", "Invest in GB"),
                    ("L. Letters", "L. Letters"),
                    ("Market Access", "Market Access"),
                    ("Selling online overseas", "Selling online overseas"),
                    ("Single sign on", "Single sign on"),
                ],
                help_text="Service to assign zendesk tickets to.",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="access_key",
            field=django_cryptography.fields.encrypt(
                models.CharField(
                    default=functools.partial(
                        django.utils.crypto.get_random_string, *(), **{"length": 64}
                    ),
                    max_length=128,
                )
            ),
        ),
    ]
