# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-21 09:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import utils.utils


class Migration(migrations.Migration):

    dependencies = [
        ('snapshot', '0022_auto_20160620_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='crop',
            field=models.ImageField(blank=True, null=True, upload_to=utils.utils.UploadPath('snapshot/photo/crops', None, 'crop', 'visitor'), verbose_name='Cropped photo'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visitor.Visitor', verbose_name='Visitor'),
        ),
    ]
