from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('book.urls')),
    path('', include('users.urls')),
    path('', include('movie.urls')),
    path('', include('TVshow.urls')),
    path('admin/', admin.site.urls),
]
