from django.urls import path
from book import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('book/', views.index, name='book_main'),
    path('admin/', admin.site.urls),
    path('search/', views.book_search, name='book_search'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
    path('add-to-list/', views.add_to_list, name='add_to_list'),
    path('delete_book/<str:book_id>/', views.delete_book, name='delete_book'),
    path('manual_book_add/', views.manual_book_add, name='manual_book_add'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)