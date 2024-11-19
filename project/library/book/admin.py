from django.contrib import admin
from .models import Name
from .models import UserBook

admin.site.register(Name)
# admin.site.register(UserBook)

class UserBookAdmin(admin.ModelAdmin):
    list_display = ( 'book_id','title', 'author', 'status', 'cover_image_url', 'added_at')
    search_fields = ('title', 'author')

admin.site.register(UserBook, UserBookAdmin)
