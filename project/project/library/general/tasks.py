from datetime import timedelta
from django.utils.timezone import now
from .models import RecentlyViewed

def clean_recently_viewed():
    threshold_date = now() - timedelta(days=2)
    RecentlyViewed.objects.filter(added_at__lt=threshold_date).delete()
    user_ids = RecentlyViewed.objects.values_list('user', flat=True).distinct()
    for user_id in user_ids:
        user_records = RecentlyViewed.objects.filter(user_id=user_id).order_by('-added_at')
        if user_records.count() > 20:
            user_records[20:].delete()