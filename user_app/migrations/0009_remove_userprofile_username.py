# Generated by Django 2.2 on 2020-11-10 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0008_auto_20201110_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='username',
        ),
    ]
