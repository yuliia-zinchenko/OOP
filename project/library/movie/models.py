from django.db import models
from django.core.exceptions import ValidationError
from general.models import MediaItem 

class Movie(MediaItem):
    """    
    @class Movie
    @brief Represents a movie added by a user.

    This model represents a movie added by a user to their collection, including its status, movie ID, release year,
    and poster URL.

    @attribute status The current status of the movie (choices: 'Watch Later', 'Watched').
    @attribute movie_id The unique identifier for the movie.
    @attribute release_year The year the movie was released.
    @attribute poster_url The URL of the movie's poster image (optional).
    """
    STATUS_CHOICES = [
        ('watch_later', 'Watch Later'),
        ('mark_as_watched', 'Watched'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watch_later')
    
    movie_id = models.IntegerField()
    release_year = models.CharField(max_length=4)
    poster_url = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        """
        @brief Specifies the uniqueness of the movie for a specific user.

        Ensures that a user can only add one instance of a movie with a particular movie ID.
        """
        unique_together = ('user', 'movie_id')
    
    def clean(self):
        """
        @brief Validates the movie's status.

        Ensures the status is one of the valid choices.

        @raise ValidationError If the status is invalid.
        """
        valid_statuses = dict(self.STATUS_CHOICES).keys()
        if self.status not in valid_statuses:
            raise ValidationError({'status': 'Invalid status choice.'})
    
    def save(self, *args, **kwargs):
        """
        @brief Validates and saves the movie instance.

        Ensures the status is valid and then saves the movie instance.

        @raise ValidationError If the status is invalid.
        """
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        """
        @brief Returns a string representation of the movie.

        @return A string representing the title of the movie and its release year.
        """
        return f"{self.title} ({self.release_year}) - {self.user.username}"


