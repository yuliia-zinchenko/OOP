from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BookSearchForm
import requests
from django.http import Http404
from html import unescape
import os
from django.http import JsonResponse
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from .models import UserBook
import json

@login_required
def index(request):
    books = UserBook.objects.all()  # Отримуємо всі книги
    return render(request, 'book/index.html', {'books': books})

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

@login_required
def book_detail(request, book_id):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}")
    if response.status_code != 200:
        raise Http404("Book not found")

    book_data = response.json()
    return render(request, 'book/book_detail.html', {'book': book_data})



@login_required
@csrf_exempt
def add_to_list(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        title = data.get('title')
        author = data.get('author')
        status = data.get('status')
        cover_image_url = data.get('cover_image_url', None) or "default_url"
        cover_image_url = unescape(cover_image_url)

        if not book_id or not status:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        # Оновлення або створення запису
        book, created = UserBook.objects.update_or_create(
            user=request.user,  
            book_id=book_id,
            defaults={
                'title': title,
                'author': author,
                'status': status,
                'cover_image_url': cover_image_url
            }
        )

        message = 'Book added successfully' if created else 'Book updated successfully'
        return JsonResponse({'message': message, 'status': status}, status=200)

    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)








