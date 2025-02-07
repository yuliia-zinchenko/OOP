from django.contrib import admin
# from .models import Name
from .models import UserBook

# admin.site.register(Name)

class UserBookAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'book_id','title', 'author', 'status', 'cover_image_url', 'added_at', 'last_updated', 'genre')
    search_fields = ('title', 'author')

admin.site.register(UserBook, UserBookAdmin)






