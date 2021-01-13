# Generated by Django 3.1.4 on 2021-01-13 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0023_auto_20210113_0954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='tags',
        ),
        migrations.AddField(
            model_name='tag',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='posts', to='blog_app.Post'),
        ),
    ]
