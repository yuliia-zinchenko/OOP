from django.contrib import admin
from .models import Name
from .models import UserBook, Quote

admin.site.register(Name)

class UserBookAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'book_id','title', 'author', 'status', 'cover_image_url', 'added_at', 'last_updated', 'genre')
    search_fields = ('title', 'author')

admin.site.register(UserBook, UserBookAdmin)

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'book_title', 'added_date',)  
    search_fields = ('text', 'book_title',)  
    list_filter = ('added_date',) 

admin.site.register(Quote, QuoteAdmin)
