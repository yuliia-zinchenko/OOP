from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils.timezone import now

class Name(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    

class UserBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=255)  
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=250, null=True, blank=True)
    genre = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50,
        choices=[
            ('read_later', 'Read Later'),
            ('currently_reading', 'Currently Reading'),
            ('mark_as_read', 'Completed')
        ]
    )
    cover_image_url = models.URLField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        self.title = self.title[:50]
        self.genre = self.genre[:250]  
        if not self.book_id:
            max_id = UserBook.objects.aggregate(Max('id'))['id__max'] or 0
            self.book_id = f"user-{max_id + 1}"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title} by {self.author}"
    class Meta:
        unique_together = ('user', 'book_id') 


class Quote(models.Model):
    text = models.TextField()
    book_title = models.CharField(max_length=255)
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} - ({self.book_title})"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=[('book', 'Book'), ('movie', 'Movie'), ('show', 'Show')])
    item_id = models.CharField(max_length=20)  # ID книги/фільму/серіалу
    title = models.CharField(max_length=255)
    viewed_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'content_type', 'item_id')



