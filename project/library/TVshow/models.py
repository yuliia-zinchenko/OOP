from django.db import models
from general.models import MediaItem

class TVshow(MediaItem):
    STATUS_CHOICES = [
        ('watch_later', 'Watch Later'),
        ('mark_as_watched', 'Watched'),
        ('currently_watching', 'Currently Watching'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watch_later')
    show_id = models.IntegerField()
    first_air_date = models.CharField(max_length=4)
    poster_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'show_id')

    def __str__(self):
        return f"{self.title} ({self.first_air_date}) - {self.user.username}"
