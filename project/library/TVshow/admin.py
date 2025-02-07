from django.contrib import admin
from .models import TVshow

class TVshowAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'show_id','title', 'status', 'poster_url','first_air_date','added_at', 'description', 'last_updated',)
    search_fields = ('title', 'author')

admin.site.register(TVshow, TVshowAdmin)
