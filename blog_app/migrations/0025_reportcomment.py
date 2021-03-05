<<<<<<< HEAD
# Generated by Django 2.2 on 2021-02-23 17:33
=======
# Generated by Django 2.2 on 2021-02-15 16:19
>>>>>>> user

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog_app', '0024_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_reports', models.IntegerField(default=0)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_comment', to='blog_app.Comment')),
                ('reports', models.ManyToManyField(blank=True, related_name='comment_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
