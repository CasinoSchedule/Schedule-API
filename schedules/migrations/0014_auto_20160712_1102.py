# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-12 18:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0013_callout'),
    ]

    operations = [
        migrations.AddField(
            model_name='callout',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 7, 12, 18, 2, 45, 249857, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='callout',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 7, 12, 18, 2, 49, 769850, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
