from django.db import models
from django.core.exceptions import ValidationError
from general.models import MediaItem 

class Movie(MediaItem):
    STATUS_CHOICES = [
        ('watch_later', 'Watch Later'),
        ('mark_as_watched', 'Watched'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watch_later')
    
    movie_id = models.IntegerField()
    release_year = models.CharField(max_length=4)
    poster_url = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'movie_id')
    
    def clean(self):
        valid_statuses = dict(self.STATUS_CHOICES).keys()
        if self.status not in valid_statuses:
            raise ValidationError({'status': 'Invalid status choice.'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.release_year}) - {self.user.username}"


