# Generated by Django 2.2 on 2020-12-15 11:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0019_auto_20201215_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportpost',
            name='reports',
            field=models.ManyToManyField(blank=True, default=0, related_name='post_reports', to=settings.AUTH_USER_MODEL),
        ),
    ]