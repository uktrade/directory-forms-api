# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-03 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_remove_client_zendesk_service_name'),
        ('submission', '0005_auto_20181205_2347'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='submission',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='submission',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='client.Client'),
        ),
    ]