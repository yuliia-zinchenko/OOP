from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
import requests
from book.models import Quote
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from django.http import Http404
from .services import get_tv_show_from_api
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date
import json
from .models import TVshow


@login_required
def TVshow_search(request):
    results = []
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

    return render(request, 'TVshow/TVshow_search.html', {'results': results, 'query': form_data})


@login_required
def show_detail(request, show_id):
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
            raise Http404("Unavaliable")

        show_data = {
            'id': api_data.get('id', 'No ID'),
            'name': api_data.get('name', 'No name'),
            'first_air_date': api_data.get('first_air_date', 'Unknown'),
            'overview': api_data.get('overview', 'Unavaliable'),
            'poster_path': f"https://image.tmdb.org/t/p/w500{api_data.get('poster_path')}" if api_data.get('poster_path') else None,
        }

    return render(request, 'tvshow/show_detail.html', {'show': show_data})


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
    elif sort_by == 'added_at':
        tvshows = tvshows.order_by('-added_at')  

    context = {
        'tvshows': tvshows,
        'status': status,
        'sort_by': sort_by, 
        'quote': quote, 
    }
    return render(request, 'tvshow/show_main.html', context)


def delete_show(request, show_id):
    if request.method == 'DELETE':
        show = get_object_or_404(TVshow, user=request.user, show_id=show_id)

        show.delete()

        return JsonResponse({'message': 'Show deleted successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

