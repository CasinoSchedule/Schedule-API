# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 00:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0019_callouttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='callout',
            name='call_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='schedules.CallOutType'),
            preserve_default=False,
        ),
    ]
