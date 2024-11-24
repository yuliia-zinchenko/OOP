import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from dotenv import load_dotenv
from datetime import date
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from .models import Movie
from django.views.decorators.csrf import csrf_exempt
from .services import get_movie_from_api
from django.http import Http404
from book.models import Quote

@login_required
def movie_search(request):
    results = []
    form_data = request.GET.get('query', '')  

    if form_data:

        load_dotenv()
        api_key = os.getenv('TMDB_API_KEY')

        url = f"https://api.themoviedb.org/3/search/movie?query={form_data}&api_key={api_key}&language=en-US"


        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
        else:
            print("API Error:", response.status_code)

    return render(request, 'movie/movie_search.html', {'results': results, 'query': form_data})




@login_required
def movie_detail(request, movie_id):
    movie = Movie.objects.filter(user=request.user, movie_id=movie_id).first()

    if movie:
        movie_data = {
            'id': movie.movie_id,
            'title': movie.title,
            'release_date': movie.release_year,
            'overview': movie.description,
            'poster_path': movie.poster_url,
        }
    else:

        api_data = get_movie_from_api(movie_id)

        if api_data is None:
            raise Http404("Фільм не знайдено або недоступний")

        movie_data = {
            'id': api_data.get('id', 'Немає назви'),
            'title': api_data.get('title', 'Немає назви'),
            'release_date': api_data.get('release_date', 'Невідомо'),
            'overview': api_data.get('overview', 'Опис недоступний'),
            'poster_path': f"https://image.tmdb.org/t/p/w500{api_data.get('poster_path')}" if api_data.get('poster_path') else None,
        }

    return render(request, 'movie/movie_detail.html', {'movie': movie_data})

@login_required
@csrf_exempt
def add_or_update_movie(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            user = request.user

            movie_id = data.get('movie_id')
            title = data.get('title')
            release_year = data.get('release_year')
            description = data.get('description', '')
            poster_url = data.get('poster_url', '')
            status = data.get('status') 

            if not movie_id or not isinstance(movie_id, int):
                return JsonResponse({"error": "Valid movie ID is required"}, status=400)
            movie, created = Movie.objects.get_or_create(
                user=user,
                movie_id=movie_id,
                defaults={
                    'title': title,
                    'release_year': release_year,
                    'description': description,
                    'poster_url': poster_url,
                    'status': status,
                }
            )

            if not created:
                # Оновлюємо статус
                movie.status = status
                movie.save()

            return JsonResponse({'message': 'Movie added or updated successfully', 'status': movie.status})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def movie_main(request):
    user = request.user

    status = request.GET.get('status')
    sort_by = request.GET.get('sort_by', 'added_at')  # За замовчуванням сортувати за датою додавання
    total_quotes = Quote.objects.count()
    if total_quotes > 0:
        quote = Quote.objects.all()[date.today().day % total_quotes] 
    else:
        quote = None
    # Фільтрація фільмів за статусом, якщо статус вказано
    movies = Movie.objects.filter(user=user)
    if status:
        movies = movies.filter(status=status)

    # Сортування фільмів
    if sort_by == 'title':
        movies = movies.order_by('title')  # Сортування за назвою
    elif sort_by == 'added_at':
        movies = movies.order_by('-added_at')  # Сортування за датою додавання (за замовчуванням)


    # Передача даних у контекст
    context = {
        'movies': movies,
        'status': status,
        'sort_by': sort_by, 
        'quote': quote, # Для активного фільтра сортування
    }
    return render(request, 'movie/movie_main.html', context)


def delete_movie(request, movie_id):
    if request.method == 'DELETE':
        movie = get_object_or_404(Movie, user=request.user, movie_id=movie_id)

        movie.delete()

        return JsonResponse({'message': 'Movie deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)



