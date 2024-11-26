import os
from dotenv import load_dotenv
import requests
import datetime

def get_tv_show_from_api(show_id):
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

