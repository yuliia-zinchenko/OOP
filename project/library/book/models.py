from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from general.models import MediaItem

class UserBook(MediaItem):
    """
    @class UserBook
    @brief Represents a book added by a user.

    This model represents a book added by a user to their collection, including details like the status of the book, 
    author, genre, and cover image. It also ensures valid status values and generates a unique book ID.

    @attribute status The current status of the book (choices: 'Read Later', 'Currently Reading', 'Completed').
    @attribute book_id The unique identifier for the book.
    @attribute author The author of the book (optional).
    @attribute genre The genre of the book (optional).
    @attribute cover_image_url The URL of the book's cover image (optional).
    """
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
        """
        @brief Validates and saves the book instance.

        Ensures the status is valid, truncates the title and genre if necessary, and generates a unique book ID if not provided.

        @raise ValueError If the status is invalid.
        """
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
        """
        @brief Returns a string representation of the book.

        @return A string representing the title and author of the book.
        """       
        
        return f"{self.title} by {self.author}"

    class Meta:
        """
        @brief Specifies the uniqueness of the book for a specific user.

        Ensures that a user can only add one instance of a book with a particular book ID.
        """        
        unique_together = ('user', 'book_id')







