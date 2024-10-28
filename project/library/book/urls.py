from django.urls import path
from book import views

urlpatterns = [
    path('book/', views.index, name='book_main')
]