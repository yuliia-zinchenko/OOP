from django.db import models
from general.models import MediaItem

class TVshow(MediaItem):
    """
    @class TVshow
    @brief Represents a TV show added by a user.

    This model represents a TV show added by a user to their collection, including its status, show ID, first air date,
    and poster URL.

    @attribute status The current status of the TV show (choices: 'Watch Later', 'Watched', 'Currently Watching').
    @attribute show_id The unique identifier for the TV show.
    @attribute first_air_date The year the show first aired.
    @attribute poster_url The URL of the TV show's poster image (optional).
    """
    STATUS_CHOICES = [
        ('watch_later', 'Watch Later'),
        ('mark_as_watched', 'Watched'),
        ('currently_watching', 'Currently Watching'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watch_later')
    show_id = models.IntegerField()
    first_air_date = models.CharField(max_length=4)
    poster_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        """
        @brief Specifies the uniqueness of the TV show for a specific user.

        Ensures that a user can only add one instance of a TV show with a particular show ID.
        """
        unique_together = ('user', 'show_id')

    def __str__(self):
        """
        @brief Returns a string representation of the TV show.

        @return A string representing the title of the TV show and its first air date.
        """
        return f"{self.title} ({self.first_air_date}) - {self.user.username}"
