# Generated by Django 2.0.2 on 2018-02-12 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteHandler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materials',
            name='material',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
