# from django.template.context_processors import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from .forms import RegisterForm
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



def index(request):
    return render(request, 'book/index.html')

def addbook(request):
    return render(request, 'book/addbook.html')

def profile_settings(request):
    return render(request, 'book/profile.html')

def user_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user=user)
            return redirect('book_main')
    return render(request, 'book/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'book/register.html'
    success_url = reverse_lazy('book_main')

    
    def form_valid(self, form):
        user = form.save()  # Зберігаємо користувача
        login(self.request, user)  # Входимо в систему з новим користувачем
        return super().form_valid(form)