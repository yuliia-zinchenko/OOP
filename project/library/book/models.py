from django.contrib.auth.models import User
from django.db import models

class Name(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    

class UserBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=255)  
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=255, null=True, blank=True)
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
    def __str__(self):
        return f"{self.title} by {self.author}"
    class Meta:
        unique_together = ('user', 'book_id') 


