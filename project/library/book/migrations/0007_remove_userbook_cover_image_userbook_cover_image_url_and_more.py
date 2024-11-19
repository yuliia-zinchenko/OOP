# Generated by Django 5.1.2 on 2024-11-19 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_userbook_cover_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbook',
            name='cover_image',
        ),
        migrations.AddField(
            model_name='userbook',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userbook',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]
