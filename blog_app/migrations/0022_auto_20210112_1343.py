# Generated by Django 3.1.4 on 2021-01-12 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0021_reportpost_total_reports'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagline', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.IntegerField(choices=[(0, 'Draft'), (1, 'Publish')], default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='blog_app.Tag'),
        ),
    ]
