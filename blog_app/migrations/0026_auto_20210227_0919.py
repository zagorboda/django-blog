# Generated by Django 2.2 on 2021-02-27 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0025_reportcomment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='active',
        ),
        migrations.AddField(
            model_name='comment',
            name='status',
            field=models.IntegerField(choices=[(0, 'Draft'), (1, 'Publish')], default=0),
        ),
    ]
