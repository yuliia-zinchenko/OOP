from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Movie(models.Model):
    STATUS_CHOICES = [
        ('watch_later', 'Watch Later'),
        ('mark_as_watched', 'Watched'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)  
    release_year = models.CharField(max_length=4)  
    description = models.TextField(blank=True, null=True)  
    poster_url = models.URLField(max_length=500, blank=True, null=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watch_later') 
    added_at = models.DateTimeField(default=timezone.now)  
    last_updated = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ('user', 'movie_id') 

    def __str__(self):
        return f"{self.title} ({self.release_year}) - {self.user.username}"


