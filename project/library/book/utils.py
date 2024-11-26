from .models import RecentlyViewed
from django.utils.timezone import now

def add_to_recently_viewed(user, content_type, item_id, title):
    # Перевіряємо, чи існує запис
    recent_item, created = RecentlyViewed.objects.update_or_create(
        user=user,
        content_type=content_type,
        item_id=item_id,
        defaults={'title': title, 'viewed_at': now()}
    )
    return recent_item

def get_recently_viewed(user, content_type=None):
    query = RecentlyViewed.objects.filter(user=user)
    if content_type:
        query = query.filter(content_type=content_type)
    return query[:20]  # Отримуємо останні 20 записів

