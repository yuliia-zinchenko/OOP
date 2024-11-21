from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BookSearchForm, ManualBookForm
import requests
from django.conf import settings
from django.http import Http404
from html import unescape
import os
from django.shortcuts import get_object_or_404
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
    query = request.GET.get('q', '').strip()  # Отримуємо пошуковий запит
    sort_by = request.GET.get('sort_by', 'date')  # Тип сортування
    status = request.GET.get('status')  # Фільтр за статусом

    books = UserBook.objects.filter(user=user).exclude(title__isnull=True).exclude(title__exact='')

    if query: 
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    if status: 
        books = books.filter(status=status)

    if sort_by == 'title':
        books = books.order_by('title')
    elif sort_by == 'author':
        books = books.order_by('author')
    elif sort_by == 'date':
        books = books.order_by('-last_updated')

    return render(request, 'book/index.html', {
        'books': books,
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
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('items', [])
        else:
            print("Error:", response.status_code)

    return render(request, 'book/book_search.html', {'form': form, 'results': results})



@login_required
def book_detail(request, book_id):
    if book_id.startswith("user-"):
        try:    
            book = UserBook.objects.get(book_id=book_id) 
        except UserBook.DoesNotExist:
            raise Http404("User book not found")
        return render(request, 'book/book_detail.html', {'book': book})

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
        genre = data.get('genre')
        cover_image_url = data.get('cover_image_url', None) or "default_url"
        cover_image_url = unescape(cover_image_url)

        if not book_id or not status:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        # Перевірка, чи book_id починається з "user_"
        if book_id.isdigit() and not book_id.startswith('user_'):
            book_id = f"user-{book_id}"

        try:
            book = UserBook.objects.get(user=request.user, book_id=book_id)
            # Якщо книга існує, оновлюємо її статус
            book.status = status
            book.last_updated = now()
            book.save()
            message = 'Book status updated successfully'
        except UserBook.DoesNotExist:
            # Якщо книга не існує, створюємо нову
            book = UserBook.objects.create(
                user=request.user,
                book_id=book_id,
                title=title,
                author=author,
                status=status,
                genre=genre,
                cover_image_url=cover_image_url,
                last_updated=now(),
            )
            message = 'Book added successfully'

        return JsonResponse({'message': message, 'status': status}, status=200)

    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)







def update_status(request, book_id):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = data['book_id']
        status = data['status']

        # Додаємо префікс до book_id, якщо він виглядає як число
        if book_id.isdigit():
            book_id = f"user_{book_id}"

        try:
            # Шукаємо книгу з відповідним book_id
            book = UserBook.objects.get(book_id=book_id)
        except UserBook.DoesNotExist:
            return JsonResponse({"error": "Book not found"}, status=404)

        # Оновлюємо статус книги
        book.status = status
        book.save()

        return JsonResponse({"status": status})



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
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            genre = form.cleaned_data['genre']
            status = form.cleaned_data['status']

            existing_book = UserBook.objects.filter(title=title, author=author).first()
            if existing_book:
                existing_book.status = status
                existing_book.save()
                message = f"Book already exists, status updated!"
            else:
                book = UserBook(
                    user=request.user,
                    title=title,
                    author=author,
                    genre=genre,
                    status=status,
                )
                book.save() 
                message = f"Book successfully added with ID {book.book_id}!"
            
            return redirect('book_main') 
    else:
        form = ManualBookForm()

    return render(request, 'book/index.html', {'form': form})



