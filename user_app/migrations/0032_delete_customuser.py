# Generated by Django 2.2 on 2020-11-14 17:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0010_auto_20201114_1731'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('user_app', '0031_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
