from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import requests
from book.models import Quote, RecentlyViewed
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from django.http import Http404
from .services import get_tv_show_from_api, get_series_by_genre
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date
import json
from .models import TVshow
from django.core.cache import cache
from book.utils import add_to_recently_viewed


@login_required
def TVshow_search(request):
    results = []
    recently_viewed_shows = RecentlyViewed.objects.filter(user=request.user, content_type='show').order_by('-viewed_at')[:20]
    form_data = request.GET.get('query', '').strip() 

    if form_data:
 
        load_dotenv()
        api_key = os.getenv('SHOW_API_KEY')

        url = f"https://api.themoviedb.org/3/search/tv?query={form_data}&api_key={api_key}&language=en-US"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', []) 
        else:
            print("API Error:", response.status_code)

    return render(request, 'TVshow/TVshow_search.html', {'results': results, 'query': form_data, 'recently_viewed_shows': recently_viewed_shows})


@login_required
def show_detail(request, show_id):
    user = request.user
    show = None  

    try:
        show = TVshow.objects.get(id=show_id, user=user)  
    except TVshow.DoesNotExist:
        show = None

    if show:
        show_data = {
            'id': show.show_id,
            'name': show.name,
            'first_air_date': show.first_air_date,
            'overview': show.description,
            'poster_path': show.poster_url,
        }
    else:

        api_data = get_tv_show_from_api(show_id)

        if api_data is None:
            raise Http404("Unavailable")

        show_data = {
            'id': api_data.get('id', 'No ID'),
            'name': api_data.get('name', 'No name'),
            'first_air_date': api_data.get('first_air_date', 'Unknown'),
            'overview': api_data.get('overview', 'Unavailable'),
            'poster_path': f"https://image.tmdb.org/t/p/w500{api_data.get('poster_path')}" if api_data.get('poster_path') else None,
        }

    cover_image_url=f"https://image.tmdb.org/t/p/w500{api_data.get('poster_path')}" if api_data.get('poster_path') else None
    add_to_recently_viewed(user, 'show', show_data['id'], show_data['name'], cover_image_url)

    return render(request, 'TVshow/show_detail.html', {'show': show_data})



@login_required
@csrf_exempt
def add_or_update_show(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user

            show_id = data.get('show_id')
            title = data.get('title')
            release_year = data.get('release_year')
            description = data.get('description', '')
            poster_url = data.get('poster_url', '')
            status = data.get('status')
            print(f"Received status: {status}") 
            print(f"Show ID: {show_id}")
            if not show_id or not isinstance(show_id, int):
                return JsonResponse({"error": "Valid show ID is required"}, status=400)

            show, created = TVshow.objects.get_or_create(
                user=user,
                show_id=show_id,
                defaults={
                    'title': title,
                    'release_year': release_year,
                    'description': description,
                    'poster_url': poster_url,
                    'status': status,
                }
            )

            if not created:
                show.status = status
                show.save()

            return JsonResponse({'message': 'TV Show added or updated successfully', 'status': show.status})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def show_main(request):
    user = request.user

    status = request.GET.get('status')
    sort_by = request.GET.get('sort_by', 'added_at')  
    total_quotes = Quote.objects.count()
    
    if total_quotes > 0:
        quote = Quote.objects.all()[date.today().day % total_quotes] 
    else:
        quote = None

    tvshows = TVshow.objects.filter(user=user)
    if status:
        tvshows = tvshows.filter(status=status)

    if sort_by == 'title':
        tvshows = tvshows.order_by('title') 
    elif sort_by == 'DATE':
        tvshows = tvshows.order_by('-last-updated')  

    context = {
        'tvshows': tvshows,
        'status': status,
        'sort_by': sort_by, 
        'quote': quote, 
    }
    return render(request, 'tvshow/show_main.html', context)

@csrf_exempt
def delete_show(request, show_id):
    if request.method == 'DELETE':
        try:
            show = get_object_or_404(TVshow, user=request.user, show_id=show_id)
            show.delete()
            return JsonResponse({'message': 'Show deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete show: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def show_recommendations(request):
    genre_id = request.GET.get('genre', '18') 
    sort_by = request.GET.get('sort_by', 'vote_average.desc')  
    page = int(request.GET.get('page', 1)) 

    if page < 1: 
        page = 1

    cache_key = f"shows_{genre_id}_{sort_by}_{page}"

    cached_shows = cache.get(cache_key)

    if cached_shows is not None:
        filtered_series = cached_shows
    else:
        saved_series_ids = set(TVshow.objects.filter(user=request.user).values_list('show_id', flat=True))


        series = get_series_by_genre(genre_id, sort_by=sort_by, page=page)

        filtered_series = [tv_show for tv_show in series if tv_show['id'] not in saved_series_ids]
        while len(filtered_series) < 20:
            page += 1  
            more_series = get_series_by_genre(genre_id, sort_by=sort_by, page=page)
            

            more_series = [tv_show for tv_show in more_series if tv_show['id'] not in saved_series_ids]
            

            filtered_series.extend(more_series)

        filtered_series = filtered_series[:20]
        cache.set(cache_key, filtered_series, timeout=600)

    genre_choices = [
        {'id': '18', 'name': 'Drama'},
        {'id': '35', 'name': 'Comedy'},
        {'id': '10765', 'name': 'Sci-Fi & Fantasy'},
        {'id': '80', 'name': 'Crime'},
        {'id': '16', 'name': 'Animation'},
    ]

    sort_choices = [
        {'id': 'vote_average.desc', 'name': 'Top Rated'},
        {'id': 'first_air_date.desc', 'name': 'Latest Releases'},
    ]


    selected_genre = next((g['name'] for g in genre_choices if g['id'] == genre_id), "Unknown Genre")

    return render(request, 'TVshow/show_recommendations.html', {
        'series': filtered_series,
        'genre_choices': genre_choices,
        'sort_choices': sort_choices,
        'selected_genre': selected_genre,
        'current_genre': genre_id,
        'current_sort': sort_by,
        'page': page,
    })





