# Generated by Django 2.2 on 2020-11-10 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0011_auto_20201110_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
