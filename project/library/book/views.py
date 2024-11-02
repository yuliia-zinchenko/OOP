from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'book/index.html')

def addbook(request):
    return render(request, 'book/addbook.html')

def profile_settings(request):
    return render(request, 'book/profile.html')

