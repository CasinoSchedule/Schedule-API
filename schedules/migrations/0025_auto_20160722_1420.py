# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-22 21:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0024_station_must_fill'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedules.Area'),
        ),
        migrations.AddField(
            model_name='shift',
            name='station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedules.Station'),
        ),
    ]
