from django.contrib import admin
from .models import Quote, RecentlyViewed

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'book_title', 'added_date',)  
    search_fields = ('text', 'book_title',)  
    list_filter = ('added_date',) 

admin.site.register(Quote, QuoteAdmin)

class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'item_id','content_type','title', 'viewed_at', 'cover_image_url')
admin.site.register(RecentlyViewed, RecentlyViewedAdmin)
