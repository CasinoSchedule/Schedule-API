# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-12 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0030_shifttemplate_starting_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='color_description',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='shifttemplate',
            name='color_description',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
