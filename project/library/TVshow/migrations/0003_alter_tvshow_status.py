# Generated by Django 5.1.2 on 2024-11-24 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TVshow', '0002_alter_tvshow_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tvshow',
            name='status',
            field=models.CharField(choices=[('watch_later', 'Watch Later'), ('mark_as_watched', 'Watched'), ('currently_watching', 'Currently Watсhing<')], default='watch_later', max_length=20),
        ),
    ]
