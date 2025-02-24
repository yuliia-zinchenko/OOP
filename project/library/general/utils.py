from .models import RecentlyViewed
from django.db import transaction

from django.db import transaction

@transaction.atomic
def add_to_recently_viewed(user, content_type, item_id, title, cover_image_url=None):
    """
    Adds a media item to the user's recently viewed list.
    
    :param user: The user who viewed the item.
    :type user: User
    :param content_type: The type of media (e.g., book, movie, TV show).
    :type content_type: str
    :param item_id: The unique ID of the media item.
    :type item_id: int
    :param title: The title of the media item.
    :type title: str
    :param cover_image_url: Optional cover image URL.
    :type cover_image_url: str or None
    """

    obj, created = RecentlyViewed.objects.update_or_create(
        user=user, content_type=content_type, item_id=item_id,
        defaults={"title": title, "cover_image_url": cover_image_url}
    )


    if created:
        excess_records = RecentlyViewed.objects.filter(
            user=user, content_type=content_type
        ).order_by('-viewed_at')[6:]


        if excess_records.exists():
            excess_records.delete()



def clean_recently_viewed():

    object_types = ['book', 'movie', 'show']
    
    for object_type in object_types:
        # Збираємо всі унікальні користувачів для цього типу
        user_ids = RecentlyViewed.objects.filter(object_type=object_type).values_list('user', flat=True).distinct()
        
        for user_id in user_ids:
            user_records = RecentlyViewed.objects.filter(user_id=user_id, object_type=object_type).order_by('-added_at')
            
            # Якщо кількість елементів перевищує 6, видаляємо найстаріші
            if user_records.count() > 6:
                records_to_delete = user_records[6:]  # Оскільки записи відсортовані від найновіших
                records_to_delete.delete()
