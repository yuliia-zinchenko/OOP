from django.urls import path
from book import views
from django.contrib import admin
from .views import RegisterView

urlpatterns = [
    path('book/', views.index, name='book_main'),
    path('admin/', admin.site.urls),
    path('addbook/', views.addbook, name='add_book'),
    path('myprofile/', views.profile_settings, name='profile_settings'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('SignUp/', RegisterView.as_view(), name='register'),

]
