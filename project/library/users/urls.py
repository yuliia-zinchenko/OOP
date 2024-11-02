from django.urls import path
from users import views
from .views import RegisterView

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('SignUp/', RegisterView.as_view(), name='register'),
    path('myprofile/', views.profile_settings, name='profile_settings'),
]