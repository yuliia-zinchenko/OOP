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
    """
    @brief Handles the main page view for the user's library.

    This view fetches the user's books, movies, and TV shows and allows for search and filtering based on status and title.
    Additionally, it displays a random quote of the day if available.

    @param request The HTTP request object.
    @return Renders the main page template with the user's library data and filters applied.
    """
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
    """
    @brief Handles the book search functionality.

    This view allows the user to search for books based on the selected search criteria (e.g., title, author).
    It integrates with the Google Books API to fetch external book data based on the search query.

    @param request The HTTP request object.
    @return Renders the book search page with the search form and the search results.
    """
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
    """
    @brief Displays the detailed page of a book.

    This view fetches the details of a specific book, either from the user's collection or the Google Books API.

    @param request The HTTP request object.
    @param book_id The unique identifier for the book.
    @return Renders the book detail page with detailed information about the book.
    """
    user = request.user
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
    cover_image_url = book_data.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail', None)
    title = book_data.get('volumeInfo', {}).get('title', 'Unknown Title')
    add_to_recently_viewed(user, 'book', book_id, title, cover_image_url)

    return render(request, 'book/book_detail.html', {'book': book_data})




@login_required
@csrf_exempt
def add_to_list(request):
    """
    @brief Adds or updates a book in the user's library.

    This view allows the user to add a book to their collection or update its status if it's already in the library.

    @param request The HTTP request object.
    @return A JSON response indicating the success or failure of the operation.
    """
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
        description = data.get('description', '')
        description = unescape(description)

        if not book_id or not status:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        if book_id.isdigit() and not book_id.startswith('user-'):
            book_id = f"user-{book_id}"

        try:
            book = UserBook.objects.get(user=request.user, book_id=book_id)
            book.status = status
            book.last_updated = now()
            book.description = description
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
                description=description,  
                last_updated=now(),
            )
            message = 'Book added successfully'

        return JsonResponse({'message': message, 'status': status}, status=200)

    return JsonResponse({'error': 'Unauthorized or invalid request'}, status=403)

def update_status(request, book_id):
    """
    @brief Updates the status of a book in the user's collection.

    This view allows the user to change the status of a book.

    @param request The HTTP request object.
    @param book_id The unique identifier for the book.
    @return A JSON response with the updated status.
    """
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
    """
    @brief Deletes a book from the user's collection.

    This view removes a book from the user's library.

    @param request The HTTP request object.
    @param book_id The unique identifier for the book.
    @return A JSON response indicating success or failure of the deletion.
    """
    if request.method == 'DELETE':
        book = get_object_or_404(UserBook, user=request.user, book_id=book_id)

        book.delete()

        return JsonResponse({'message': 'Book deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    



def manual_book_add(request):
    """
    @brief Manually adds a book to the user's library.

    This view allows the user to manually enter details for a book to add to their library.

    @param request The HTTP request object.
    @return Renders the book index page with the form or redirects after a successful add.
    """
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
    """
    @brief Displays book recommendations for the user.

    This view suggests books based on the user's genre preferences and past behavior.

    @param request The HTTP request object.
    @return Renders the recommendations page with the suggested books.
    """
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


