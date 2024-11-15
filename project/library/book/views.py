from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BookSearchForm
import requests
from django.http import Http404
import os
from dotenv import load_dotenv

@login_required
def index(request):
    return render(request, 'book/index.html')

@login_required
def profile_settings(request):
    return render(request, 'book/profile.html')

@login_required
def book_search(request):
    results = []
    form = BookSearchForm(request.GET) 
    


    if request.method == "GET" and form.is_valid():
        query = form.cleaned_data['query']
        load_dotenv()
        api_key = os.getenv('api_key')
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&langRestrict=en&key={api_key}'
        print("API Key:", api_key)
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('items', [])
        else:
            print("Error:", response.status_code)

    return render(request, 'book/book_search.html', {'form': form, 'results': results})


def book_detail(request, book_id):
    # Замініть API-запит на свій власний метод отримання даних
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}")
    if response.status_code != 200:
        raise Http404("Book not found")

    book_data = response.json()
    return render(request, 'book/book_detail.html', {'book': book_data})


