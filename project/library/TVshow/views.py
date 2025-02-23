from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import requests
from general.models import Quote, RecentlyViewed
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
from general.utils import add_to_recently_viewed



@login_required
def TVshow_search(request):
    """
    @brief Handles the TV show search functionality.

    This view allows users to search for TV shows based on a query. It retrieves results 
    from an external API and displays them, along with the user's recently viewed shows.

    @param request The HTTP request object.
    @return Renders the TV show search page with search results and recent shows.
    """
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
            error_message = f"API Error: {response.status_code}"
            print(error_message)
            return render(request, 'TVshow/TVshow_search.html', {'results': results, 'query': form_data, 'recently_viewed_shows': recently_viewed_shows, 'error_message': error_message})

    return render(request, 'TVshow/TVshow_search.html', {'results': results, 'query': form_data, 'recently_viewed_shows': recently_viewed_shows})


@login_required
def show_detail(request, show_id):
    """
    @brief Displays the details of a specific TV show.

    This view either retrieves TV show details from the database if the user has added 
    it or fetches data from an external API. It also adds the show to the user's recently viewed list.

    @param request The HTTP request object.
    @param show_id The ID of the TV show.
    @return Renders the show detail page with the TV show data.
    """
    user = request.user
    show = None  

    try:
        show = TVshow.objects.get(id=show_id, user=user)  
    except TVshow.DoesNotExist:
        show = None

    if show:
        show_data = {
            'id': show.show_id,
            'name': show.title,
            'first_air_date': show.first_air_date,
            'overview': show.description,
            'poster_path': show.poster_url,
        }
        cover_image_url = show.poster_url
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
        cover_image_url = show_data['poster_path']

    #cover_image_url=f"https://image.tmdb.org/t/p/w500{api_data.get('poster_path')}" if api_data.get('poster_path') else None
    add_to_recently_viewed(user, 'show', show_data['id'], show_data['name'], cover_image_url)

    return render(request, 'TVshow/show_detail.html', {'show': show_data})



@login_required
@csrf_exempt
def add_or_update_show(request):
    """
    @brief Adds or updates a TV show for the user.

    This view processes the incoming data for adding a new show or updating an existing 
    show's status. It returns a JSON response indicating success or failure.

    @param request The HTTP request object containing the show data.
    @return JSON response with a success or error message.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user

            show_id = data.get('show_id')
            title = data.get('title')
            first_air_date = data.get('first_air_date')
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
                    'first_air_date': first_air_date,
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
    """
    @brief Displays the main TV show page with a list of user's shows.

    This view renders a list of TV shows that the user has added, with the option to 
    filter by status and sort by title or date. It also includes a random quote for the day.

    @param request The HTTP request object.
    @return Renders the main page with the user's TV shows, sorted and filtered.
    """
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
    elif sort_by == 'date':
        tvshows = tvshows.order_by('-last_updated')  

    context = {
        'tvshows': tvshows,
        'status': status,
        'sort_by': sort_by, 
        'quote': quote, 
    }
    return render(request, 'tvshow/show_main.html', context)

@csrf_exempt
def delete_show(request, show_id):
    """
    @brief Deletes a TV show for the user.

    This view deletes a TV show from the user's list. It returns a JSON response 
    indicating success or failure.

    @param request The HTTP request object.
    @param show_id The ID of the show to delete.
    @return JSON response with a success or error message.
    """
    if request.method == 'DELETE':
        try:
            show = get_object_or_404(TVshow, user=request.user, show_id=show_id)
            show.delete()
            return JsonResponse({'message': 'Show deleted successfully'}, status=200)
        except Http404:
            return JsonResponse({'error': 'Failed to delete show: Show matching query does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete show: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def show_recommendations(request):
    """
    @brief Displays TV show recommendations based on genre and sorting options.

    This view retrieves TV shows based on the selected genre and sort criteria, 
    filtering out shows the user has already added to their list. The results are 
    cached to improve performance.

    @param request The HTTP request object containing the genre and sorting options.
    @return Renders the recommendations page with a list of filtered TV shows.
    """
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





