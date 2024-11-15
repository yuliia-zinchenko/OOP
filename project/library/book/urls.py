from django.urls import path
from book import views
from django.contrib import admin



urlpatterns = [
    path('book/', views.index, name='book_main'),
    path('admin/', admin.site.urls),
    path('search/', views.book_search, name='book_search'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
]
