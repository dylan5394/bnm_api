# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-03 02:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_brickandmortruser_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Designer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('m', 'men'), ('w', 'women')], default='m', max_length=1)),
                ('name', models.CharField(max_length=100)),
                ('image', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='designer_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='designer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Designer'),
        ),
    ]
