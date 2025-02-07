from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max

# class Name(models.Model):
#     name = models.CharField(max_length=50)
#     def __str__(self):
#         return self.name
    

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
        valid_statuses = ['read_later', 'currently_reading', 'mark_as_read']
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Allowed values are {valid_statuses}")
        self.title = self.title[:50]
        if self.genre:  # Перевірка, чи не є None
            self.genre = self.genre[:250] 
        if not self.book_id:
            max_id = UserBook.objects.filter(user=self.user).aggregate(Max('id'))['id__max'] or 0
            self.book_id = f"user-{self.user.id}-{max_id + 1}"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.title} by {self.author}"
    class Meta:
        unique_together = ('user', 'book_id') 






