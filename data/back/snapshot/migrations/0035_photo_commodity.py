# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-11 11:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20160527_0749'),
        ('snapshot', '0034_auto_20160711_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='commodity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Commodity'),
        ),
    ]
