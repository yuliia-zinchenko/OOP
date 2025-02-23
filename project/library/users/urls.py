from django.urls import path
from users import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('SignUp/', views.register, name='register'),
    path('myprofile/', views.profile_settings, name='profile_settings'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm')
]