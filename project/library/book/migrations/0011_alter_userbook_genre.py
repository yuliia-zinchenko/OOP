# Generated by Django 5.1.2 on 2024-11-21 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0010_userbook_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbook',
            name='genre',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
