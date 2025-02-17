from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BookSearchForm, ManualBookForm
import requests
from django.http import Http404
from html import unescape
import os
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from .models import UserBook
from general.models import Quote, RecentlyViewed
from movie.models import Movie
from TVshow.models import TVshow
from datetime import date
from django.db.models import Q
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from .services import get_top_genres, get_recommendations_from_google_books, get_bestsellers_with_google_info, get_author_based_recommendations_with_api
from itertools import chain
from general.utils import add_to_recently_viewed


@login_required
def index(request):
    user = request.user
    query = request.GET.get('q', '').strip()  
    sort_by = request.GET.get('sort_by', 'date')  
    status = request.GET.get('status') 
    total_quotes = Quote.objects.count()
    if total_quotes > 0:
        quote = Quote.objects.all()[date.today().day % total_quotes] 
    else:
        quote = None

    books = UserBook.objects.filter(user=user).exclude(title__isnull=True).exclude(title__exact='')
    movies = Movie.objects.filter(user=user)
    tvshows = TVshow.objects.filter(user=user)

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        movies = movies.filter(
            Q(title__icontains=query) | Q(release_year__icontains=query)
        )
        tvshows = tvshows.filter(
            Q(title__icontains=query) | Q(first_air_date__icontains=query)
        )
        

        results = sorted(
            list(chain(books, movies, tvshows)),
            key=lambda x: x.title if hasattr(x, 'title') else '',
        )
    else:

        results = []

    # Сортування книг
    if sort_by == 'title':
        books = books.order_by('title')
    elif sort_by == 'author':
        books = books.order_by('author')
    elif sort_by == 'date':
        books = books.order_by('-last_updated')

    # Фільтрація за статусом
    if status:
        books = books.filter(status=status)

    return render(request, 'book/index.html', {
        'books': books,  
        'movies': movies,  
        'results': results, 
        'sort_by': sort_by,
        'status': status,
        'query': query,
        'quote': quote,
    })


@login_required
def book_search(request):
    results = []
    recently_viewed_books = RecentlyViewed.objects.filter(user=request.user, content_type='book').order_by('-viewed_at')[:20]
    form = BookSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data['query']
        search_by = form.cleaned_data['search_by']
        load_dotenv()
        api_key = os.getenv('api_key')

        url = f'https://www.googleapis.com/books/v1/volumes'
        params = {
            'q': f'{search_by}:{query}',
            'langRestrict': 'en',
            'key': api_key,
            'maxResults': 40 
        }

        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('items', [])
        else:
            print("Error:", response.status_code)

    return render(request, 'book/book_search.html', {'form': form, 'results': results, 'recently_viewed_books': recently_viewed_books})



@login_required 
def book_detail(request, book_id):
    user = request.user

    if book_id.startswith("user-"):
        try:    
            book = UserBook.objects.get(book_id=book_id) 
        except UserBook.DoesNotExist:
            raise Http404("User book not found")

        # add_to_recently_viewed(user, 'book', book.id, book.title)

        return render(request, 'book/book_detail.html', {'book': book})

    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{book_id}")
    if response.status_code != 200:
        raise Http404("Book not found")

    book_data = response.json()
    cover_image_url = book_data.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail', None)
    title = book_data.get('volumeInfo', {}).get('title', 'Unknown Title')
    add_to_recently_viewed(user, 'book', book_id, title, cover_image_url)

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

        if book_id.isdigit() and not book_id.startswith('user-'):
            book_id = f"user-{book_id}"

        try:
            book = UserBook.objects.get(user=request.user, book_id=book_id)
            book.status = status
            book.last_updated = now()
            book.save()
            message = 'Book status updated successfully'
        except UserBook.DoesNotExist:
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

        if book_id.isdigit():
            book_id = f"user_{book_id}"

        try:

            book = UserBook.objects.get(book_id=book_id)
        except UserBook.DoesNotExist:
            return JsonResponse({"error": "Book not found"}, status=404)

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

def recommendations(request):
    user = request.user

    top_genres = get_top_genres(user)
    recommended_books = get_recommendations_from_google_books(top_genres, min_rating=4.0, max_results=5)

    author_based = get_author_based_recommendations_with_api(user)

    best_sellers = get_bestsellers_with_google_info() 

    error_message = None
    if not best_sellers:
        error_message = 'No bestsellers found'
    
    return render(request, 'book/recommendations.html', {
        'recommended_books': recommended_books,
        'author_based': author_based,
        'best_sellers': best_sellers,
        'error_message': error_message,
    })


