from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

class Quote(models.Model):
    text = models.TextField()
    book_title = models.CharField(max_length=255)
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} - ({self.book_title})"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=[('book', 'Book'), ('movie', 'Movie'), ('show', 'Show')])
    item_id = models.CharField(max_length=20) 
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True, null=True)
    viewed_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'content_type', 'item_id')
