# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-12 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0022_auto_20160727_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managerprofile',
            name='position_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
