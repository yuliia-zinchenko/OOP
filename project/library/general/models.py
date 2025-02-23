from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils import timezone
"""
Library Management System

This module contains models for managing books, movies, TV shows, and user interactions.
"""


class Quote(models.Model):
    """
     @class Quote
     @brief A model that stores quotes from books in the system.
     
     This model contains the text of the quote, the title of the book from which
     the quote is taken, and the date when the quote was added to the system.
     
     @attribute text The text of the quote.
     @attribute book_title The title of the book from which the quote is taken.
     @attribute added_date The date when the quote was added to the system (automatically set when added).
     """
    text = models.TextField()
    book_title = models.CharField(max_length=255)
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} - ({self.book_title})"


class RecentlyViewed(models.Model):
    """
    @class RecentlyViewed
    @brief A model that stores recently viewed media items by a user.
    
    This model keeps track of media items (book, movie, or show) that a user has recently viewed,
    including the item's title, content type, cover image URL, and the timestamp of when it was viewed.
    
    @attribute user The user who viewed the media item (ForeignKey to User model).
    @attribute content_type The type of the media item (Book, Movie, or Show).
    @attribute item_id The unique identifier for the media item.
    @attribute title The title of the media item.
    @attribute cover_image_url The URL of the media item's cover image (optional).
    @attribute viewed_at The timestamp when the media item was viewed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=[('book', 'Book'), ('movie', 'Movie'), ('show', 'Show')])
    item_id = models.CharField(max_length=20) 
    title = models.CharField(max_length=255)
    cover_image_url = models.URLField(blank=True, null=True)
    viewed_at = models.DateTimeField(default=now)

    class Meta:
        """
        @brief Specifies the ordering and uniqueness of the RecentlyViewed model.
        
        The items are ordered by `viewed_at` in descending order.
        The combination of `user`, `content_type`, and `item_id` must be unique.
        """
        ordering = ['-viewed_at']
        unique_together = ('user', 'content_type', 'item_id')

class MediaItem(models.Model):
    """
    @class MediaItem
    @brief Abstract base class representing a general media item.

    This model serves as a base class for various types of media items, such as books, movies, or shows.
    It contains the common attributes for all media items, such as user, title, description, status, and timestamps.
    
    @attribute user The user associated with the media item (ForeignKey to User model).
    @attribute title The title of the media item.
    @attribute description A brief description of the media item (optional).
    @attribute status The current status of the media item (e.g., 'read', 'watched', 'to-do').
    @attribute added_at The timestamp when the media item was added to the system.
    @attribute last_updated The timestamp when the media item was last updated.
    
    @note This is an abstract class and cannot be instantiated directly.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)  
    added_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        """
        @brief Specifies this model as an abstract base class.
        
        This model will not create its own database table. It is meant to be inherited by other models.
        """
        abstract = True  

    def __str__(self):
        """
        @brief Returns a string representation of the media item.
        
        This method returns the title of the media item as its string representation.
        
        @return A string containing the title of the media item.
        """
        return self.title

