# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 10:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import utils.utils
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('visitor', '0002_visitor_weixin'),
        ('snapshot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=160, verbose_name='Message')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('modify_data', models.DateTimeField(auto_now=True, verbose_name='Date modified')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visitor.Visitor', verbose_name='Author')),
            ],
            options={
                'ordering': ('create_date', 'pk'),
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.AlterModelOptions(
            name='photo',
            options={'ordering': ('create_date', 'pk'), 'verbose_name': 'Photo', 'verbose_name_plural': 'Photos'},
        ),
        migrations.AlterField(
            model_name='mirror',
            name='owner',
            field=models.ForeignKey(help_text='Mirror`s last user', null=True, on_delete=django.db.models.deletion.CASCADE, to='visitor.Visitor', verbose_name='Mirror`s owner'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='visitor.Visitor', verbose_name='Photo owner'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=utils.utils.UploadPath('mirror/photo', 'owner'), validators=[utils.validators.SizeValidator(2)], verbose_name='Photo'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumb',
            field=models.ImageField(blank=True, null=True, upload_to=utils.utils.UploadPath('mirror/photo/thumbs', 'owner', suff='thumb'), verbose_name='Thumbnail'),
        ),
        migrations.AddField(
            model_name='comment',
            name='photo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snapshot.Photo', verbose_name='Photo'),
        ),
    ]
