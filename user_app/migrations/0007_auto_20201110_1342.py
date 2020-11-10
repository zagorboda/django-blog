# Generated by Django 2.2 on 2020-11-10 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0006_auto_20201110_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='name',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(default=False, max_length=100, primary_key=True, serialize=False, unique=True),
        ),
    ]
