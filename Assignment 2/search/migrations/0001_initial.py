# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-04 12:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sym_key_cons', models.CharField(max_length=1024)),
                ('client_bucket', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Consultant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('public_exp', models.CharField(max_length=1024)),
                ('public_mod', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=1024)),
                ('amount_bucket', models.CharField(max_length=1)),
                ('date_bucket', models.CharField(max_length=1)),
                ('client_bucket', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='consultant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='search.Consultant'),
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]