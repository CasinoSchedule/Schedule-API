# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-08 18:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0029_remove_shifttemplate_starting_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='shifttemplate',
            name='starting_time',
            field=models.TimeField(default='11:00'),
            preserve_default=False,
        ),
    ]
