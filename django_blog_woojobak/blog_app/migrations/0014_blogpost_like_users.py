# Generated by Django 4.2.5 on 2023-10-03 13:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog_app', '0013_remove_blogpost_like_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='like_users',
            field=models.ManyToManyField(related_name='like_articles', to=settings.AUTH_USER_MODEL),
        ),
    ]
