from django.http import HttpResponse
from django.template.context_processors import request
from django.shortcuts import render

def index(request):
    return render(request, 'book/index.html')

