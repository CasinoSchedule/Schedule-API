# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-25 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0025_auto_20160722_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='must_fill',
            field=models.NullBooleanField(),
        ),
    ]