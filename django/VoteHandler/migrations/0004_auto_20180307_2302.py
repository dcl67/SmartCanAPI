# Generated by Django 2.0.2 on 2018-03-08 04:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteHandler', '0003_auto_20180215_0243'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Configuration',
        ),
        migrations.AlterField(
            model_name='disposablevote',
            name='count',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
