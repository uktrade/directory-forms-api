# Generated by Django 4.2.11 on 2024-05-20 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0014_auto_20191021_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='data',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='submission',
            name='meta',
            field=models.JSONField(),
        ),
    ]
