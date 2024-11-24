import os
from dotenv import load_dotenv
import requests

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
