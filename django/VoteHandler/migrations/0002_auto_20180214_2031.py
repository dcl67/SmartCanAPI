# Generated by Django 2.0.2 on 2018-02-15 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteHandler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_id', models.UUIDField(verbose_name='Smartcan ID')),
                ('config', models.TextField(max_length=4096)),
            ],
        ),
        migrations.AlterField(
            model_name='disposablevote',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]