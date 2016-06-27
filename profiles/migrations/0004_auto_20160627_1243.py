# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-27 19:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0006_shift'),
        ('profiles', '0003_auto_20160624_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='employeeprofile',
            name='days_off',
            field=models.ManyToManyField(blank=True, null=True, to='schedules.DayOfWeek'),
        ),
        migrations.AddField(
            model_name='employeeprofile',
            name='employment_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.EmployeeStatus'),
        ),
    ]