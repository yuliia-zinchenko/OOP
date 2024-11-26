from django.urls import path
from movie import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('movie_search/', views.movie_search, name='movie_search'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('add_or_update_movie/', views.add_or_update_movie, name='add_or_update_movie'),
    path('movie/', views.movie_main, name='movie_main'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('movie_recommendations/', views.movie_recommendations, name='movie_recommendations'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)