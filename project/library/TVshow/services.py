import os
from dotenv import load_dotenv
import requests
import datetime

def get_tv_show_from_api(show_id):
    """
        @brief Fetches TV show details from TMDB API.

        This function queries TMDB API using the given TV show title and retrieves
        information such as season count, first air date, genres, and poster image.
    
        @param title The title of the TV show to search for.
        @return A JSON string containing TV show details.
    
        @note Requires an active internet connection.
        @warning API key must be correctly set up.
        @warning API rate limits may apply.
    """

    load_dotenv()
    api_key = os.getenv('SHOW_API_KEY')
    url = f"https://api.themoviedb.org/3/tv/{show_id}"
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
    


def get_series_by_genre(genre, sort_by="popularity.desc", page=1):
    api_url = f"https://api.themoviedb.org/3/discover/tv"
    load_dotenv()
    api_key = os.getenv('SHOW_API_KEY')
    current_year = datetime.datetime.now().year

    params = {
        "api_key": api_key,
        "with_genres": genre,  
        "sort_by": sort_by, 
        "page": page,
        "language": "en-US",
        "vote_count.gte": 300,  
        "first_air_date.lte": f"{current_year}-12-31",  
    }
    
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")
        return []

