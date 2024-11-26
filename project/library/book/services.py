import requests
import os
from dotenv import load_dotenv
from django.db.models import Count
from django.db.utils import IntegrityError
from .models import UserBook
from movie.models import Movie
from TVshow.models import TVshow

def get_top_genres(user, top_n=3):
    top_genres = UserBook.objects.filter(user=user, status='mark_as_read') \
                                  .values('genre') \
                                  .annotate(count=Count('genre')) \
                                  .order_by('-count')[:top_n]
    return [genre['genre'] for genre in top_genres]

from django.core.cache import cache


def get_recommendations_from_google_books(genres, min_rating=4.0, max_results=10, cache_timeout=3600):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    api_url = 'https://www.googleapis.com/books/v1/volumes'

    recommended_books = []

    for genre in genres:
        # Перевірити, чи є дані в кеші
        cache_key = f"recommendations_{genre}_{min_rating}"
        cached_data = cache.get(cache_key)

        if cached_data:
            print(f"Using cached data for genre: {genre}")
            recommended_books.extend(cached_data)
            continue

        # Якщо немає в кеші, робимо запит до API
        response = requests.get(api_url, params={
            'q': f'subject:{genre}+averageRating>={min_rating}',
            'orderBy': 'relevance',
            'langRestrict': 'en',
            'key': api_key,
            'maxResults': max_results
        })

        if response.status_code == 200:
            data = response.json()
            books = data.get('items', [])
            books_data = [
                {
                    'id': book.get('id'),
                    'title': book.get('volumeInfo', {}).get('title', 'Unknown Title'),
                    'author': ', '.join(book.get('volumeInfo', {}).get('authors', ['Unknown Author'])),
                    'genre': genre,
                    'cover_image_url': book.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail', ''),
                    'link': book.get('volumeInfo', {}).get('infoLink', '#'),
                }
                for book in books
            ]

            # Зберігаємо результати в кеш
            cache.set(cache_key, books_data, timeout=cache_timeout)
            recommended_books.extend(books_data)
        else:
            print(f"API Error: {response.status_code}, {response.text}")

    return recommended_books




def get_best_sellers():
    api_key = os.getenv('NYT_API_KEY') 
    url = "https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json"
    params = {'api-key': api_key}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        books = data.get('results', {}).get('books', [])
        return books
    else:
        print(f"Error fetching bestsellers: {response.status_code}")
        return []
    
def get_book_info_from_google(title):
    api_key = os.getenv('api_key')
    url = f"https://www.googleapis.com/books/v1/volumes"
    
    params = {
        'q': title, 
        'key': api_key
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            return data['items'][0]  
    else:
        print(f"Error fetching book info from Google: {response.status_code}")
        return None
    
    
def get_bestsellers_with_google_info():
    best_sellers = get_best_sellers()
    books_with_details = []

    for book in best_sellers:
        book_title = book.get('title')  
        book_info = get_book_info_from_google(book_title)
        
        if book_info:
            volume_info = book_info.get('volumeInfo', {})
            books_with_details.append({
                'id': book_info['id'],  
                'title': volume_info.get('title', 'Unknown Title'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                'link': volume_info.get('infoLink', '#'),
                'genre': book.get('genre', 'Unknown Genre')
            })
    
    return books_with_details


def get_daily_quote():
    url = "https://api.quotable.io/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "text": data["content"],
            "author": data["author"]
        }
    else:
        return None
    

def get_author_based_recommendations(user):
    favorite_authors = UserBook.objects.filter(user=user).exclude(author__isnull=True).exclude(author__exact='').values_list('author', flat=True).distinct()

    author_recommendations = UserBook.objects.filter(author__in=favorite_authors).exclude(user=user)


    recommendations = author_recommendations 

    return recommendations.distinct()

def search_books_by_author(author_name):
    url = f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{author_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        books_data = response.json()
        return [
            {
                'id': item.get('id'), 
                "title": item.get("volumeInfo", {}).get("title", ""),
                "author": ", ".join(item.get("volumeInfo", {}).get("authors", [])),
                "description": item.get("volumeInfo", {}).get("description", ""),
                'cover_image_url': item.get("volumeInfo", {}).get('imageLinks', {}).get('thumbnail', ''),
                "genre": item.get("volumeInfo", {}).get("categories", [])[0] if item.get("volumeInfo", {}).get("categories") else "Unknown",
            }
            for item in books_data.get("items", [])
        ]
    return []

def get_author_based_recommendations_with_api(user):

    favorite_authors = (
        UserBook.objects.filter(user=user)
        .exclude(author__isnull=True)
        .exclude(author__exact='')
        .values('author')
        .annotate(author_count=Count('author'))
        .filter(author_count__gte=2)
        .values_list('author', flat=True)
    )

    author_recommendations = []
    for author in favorite_authors:
        books_by_author = (
            UserBook.objects.filter(author=author)
            .exclude(user=user)
            .order_by('title')[:3]
        )
        author_recommendations.extend(books_by_author)

    api_recommendations = []
    for author in favorite_authors:
        api_books = search_books_by_author(author)[:3] 
        api_recommendations.extend(api_books)


    recommendations = list(author_recommendations) + api_recommendations


    return recommendations



