from django.contrib import admin
from .models import Movie

class MovieAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'movie_id','title', 'status', 'poster_url','release_year','added_at', 'description', 'last_updated',)
    search_fields = ('title', 'author')

admin.site.register(Movie, MovieAdmin)


