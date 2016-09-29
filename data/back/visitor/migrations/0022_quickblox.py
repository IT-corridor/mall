# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-29 11:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('visitor', '0021_auto_20160826_2101'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quickblox',
            fields=[
                ('qid', models.PositiveIntegerField(verbose_name='Quickblox external ID')),
                ('login', models.CharField(max_length=50, verbose_name='Login')),
                ('full_name', models.CharField(max_length=50, verbose_name='Full name')),
                ('password', models.CharField(max_length=50, verbose_name='Password')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('pk',),
                'verbose_name': 'Quickblox',
            },
        ),
    ]
