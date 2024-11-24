import requests
import os
from dotenv import load_dotenv

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
