# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-01 01:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_remove_employeeprofile_days_off'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofile',
            name='first_name',
            field=models.CharField(default='John', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employeeprofile',
            name='last_name',
            field=models.CharField(default='Smith', max_length=255),
            preserve_default=False,
        ),
    ]
