from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BookSearchForm, ManualBookForm
import requests
from django.http import Http404
from html import unescape
import os
from django.http import JsonResponse
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from .models import UserBook
from django.db.models import Q
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from datetime import datetime

@login_required
# def index(request):
#     user = request.user
#     books = UserBook.objects.filter(user=user)

#     query = request.GET.get('q')
#     if query:
#         books = books.filter(
#             Q(title__icontains=query) | Q(author__icontains=query)
#         )

#     status = request.GET.get('status')
#     if status:
#         books = books.filter(status=status)

#     sort_by = request.GET.get('sort_by', 'date')
#     if sort_by == 'title':
#         books = books.order_by('title') 
#     elif sort_by == 'author':
#         books = books.order_by('author')  
#     else:
#         books = books.order_by('-last_updated') 

#     return render(request, 'book/index.html', {
#         'books': books,
#         'sort_by': sort_by,
#         'status': status,
#         'query': query,
#     })

def index(request):
    user = request.user
    books = UserBook.objects.filter(user=user)

    # Пошук по запиту
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    # Фільтрація по статусу
    status = request.GET.get('status')
    if status:
        books = books.filter(status=status)

    # Сортування
    sort_by = request.GET.get('sort_by', 'date')
    if sort_by == 'title':
        books = books.order_by('title')
    elif sort_by == 'author':
        books = books.order_by('author')
    else:
        books = books.order_by('-last_updated')

    # Отримуємо книги з API (якщо вони є)
    load_dotenv()
    api_key = os.getenv('API_KEY')
    api_url = 'https://www.googleapis.com/books/v1/volumes'
    response = requests.get(api_url, params={'q': query, 'key': api_key})
    
    api_books = []
    if response.status_code == 200:
        data = response.json()
        api_books = data.get('items', [])

    # Об'єднуємо книги з бази та книги з API
    all_books = list(books) + api_books

    return render(request, 'book/index.html', {
        'books': all_books,
        'sort_by': sort_by,
        'status': status,
        'query': query,
    })



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
        title = unescape(title)
        author = data.get('author')
        status = data.get('status')
        cover_image_url = data.get('cover_image_url', None) or "default_url"
        cover_image_url = unescape(cover_image_url)

        if not book_id or not status:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        book, created = UserBook.objects.update_or_create(
            user=request.user,  
            book_id=book_id,
            defaults={
                'title': title,
                'author': author,
                'status': status,
                'cover_image_url': cover_image_url,
                "last_updated": now(), 
            }
        )

        if not created: 
            book.status = status
            book.last_updated = now()
            book.save()

        message = 'Book added successfully' if created else 'Book updated successfully'
        return JsonResponse({'message': message, 'status': status}, status=200)

    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)


def update_status(request, book_id):
    book = get_object_or_404(UserBook, id=book_id)
    if request.method == "POST":
        book.status = request.POST.get('status')
        book.last_updated = now() 
        book.save()
        return redirect('book_detail', book_id=book.id)


def delete_book(request, book_id):
    if request.method == 'DELETE':
        book = get_object_or_404(UserBook, user=request.user, book_id=book_id)

        book.delete()

        return JsonResponse({'message': 'Book deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    


def manual_book_add(request):
    if request.method == "POST":
        form = ManualBookForm(request.POST)
        if form.is_valid():
            # Отримуємо дані з форми
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            
            # Перевірка на наявність книги в базі даних
            existing_book = UserBook.objects.filter(title=title, author=author).first()
            
            # Якщо книга вже є в базі, просто оновлюємо її дані
            if existing_book:
                existing_book.save()
                message = "Book already exists, but we have updated the information!"
            else:
                # Додаємо нову книгу
                book = UserBook(
                    user=request.user,
                    title=title,
                    author=author,
                    cover_image_url="default_book_cover_url",  # Встановлюємо стандартну обкладинку
                    status="not_started",  # За замовчуванням, користувач може змінити статус
                    last_updated=datetime.now()
                )
                book.save()
                message = "Book successfully added to your library!"
            
            return render(request, 'book/index.html', {'message': message})

    else:
        form = ManualBookForm()

    return render(request, 'book/manual_book_add.html', {'form': form})


