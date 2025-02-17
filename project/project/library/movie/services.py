import requests
import os
from dotenv import load_dotenv
import datetime


def get_movie_from_api(movie_id):
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')  
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    params = {
        'api_key': api_key,
        'language': 'en-US',
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return response.json()  
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    
def get_movies_by_genre(genre, sort_by="popularity", page=1, min_results=20):
    import datetime
    import requests
    from dotenv import load_dotenv
    import os

    api_url = f"https://api.themoviedb.org/3/discover/movie"
    load_dotenv()
    api_key = os.getenv('TMDB_API_KEY')
    current_year = datetime.datetime.now().year

    results = [] 

    while len(results) < min_results:
        params = {
            "api_key": api_key,
            "with_genres": genre,  
            "sort_by": sort_by, 
            "page": page,
            "language": "en-US",
            "vote_count.gte": 700,
            "primary_release_date.lte": f"{current_year}-12-31",
        }
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])
            results.extend(movies)
            
            # Перевірка, чи є більше сторінок
            if page >= data.get('total_pages', 0):
                break
            page += 1 
        else:
            break 

        # Якщо менше 20 результатів, запитуємо ще раз
        if len(results) < min_results and page >= data.get('total_pages', 0):
            page = 1  # Скидаємо на першу сторінку, щоб отримати нові результати

    # Повертаємо лише перші 20 результатів
    return results[:min_results]


    
