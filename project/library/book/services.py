import requests
import os
from dotenv import load_dotenv
from django.db.models import Count
from .models import UserBook

def get_top_genres(user, top_n=3):
    top_genres = UserBook.objects.filter(user=user, status='mark_as_read') \
                                  .values('genre') \
                                  .annotate(count=Count('genre')) \
                                  .order_by('-count')[:top_n]
    return [genre['genre'] for genre in top_genres]

def get_recommendations_from_google_books(genres):
    load_dotenv()
    api_key = os.getenv('API_KEY')
    api_url = 'https://www.googleapis.com/books/v1/volumes'

    recommended_books = []
    for genre in genres:
        response = requests.get(api_url, params={'q': f'subject:{genre}', 'key': api_key, 'maxResults': 5})
        if response.status_code == 200:
            data = response.json()
            books = data.get('items', [])
            for book in books:
                volume_info = book.get('volumeInfo', {})
                recommended_books.append({
                    'id': book.get('id'), 
                    'title': volume_info.get('title', 'Unknown Title'),
                    'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                    'genre': genre,
                    'cover_image_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    'link': volume_info.get('infoLink', '#'),
                })
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
