from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from general.models import MediaItem

class UserBook(MediaItem):
    STATUS_CHOICES = [
        ('read_later', 'Read Later'),
        ('currently_reading', 'Currently Reading'),
        ('mark_as_read', 'Completed')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    book_id = models.CharField(max_length=255)
    author = models.CharField(max_length=250, null=True, blank=True)
    genre = models.CharField(max_length=250, null=True, blank=True)
    cover_image_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        valid_statuses = ['read_later', 'currently_reading', 'mark_as_read']
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Allowed values are {valid_statuses}")
        self.title = self.title[:50]
        if self.genre:
            self.genre = self.genre[:250]
        if not self.book_id:
            max_id = UserBook.objects.filter(user=self.user).aggregate(Max('id'))['id__max'] or 0
            self.book_id = f"user-{self.user.id}-{max_id + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        unique_together = ('user', 'book_id')







