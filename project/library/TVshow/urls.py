from django.urls import path
from TVshow import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('TVshow_search/', views.TVshow_search, name='TVshow_search'),
    path('TVshow/<int:show_id>/', views.show_detail, name='show_detail'),
    path('add_or_update_tvshow/', views.add_or_update_show, name='add_or_update_show'),
    path('show/', views.show_main, name='show_main'),
    path('delete_show/<int:show_id>/', views.delete_show, name='delete_show'),
    path('show_recommendations/', views.show_recommendations, name='show_recommendations'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)