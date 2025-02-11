from django.test import TestCase
from django.contrib.auth.models import User
from .models import TVshow
from django.utils import timezone
from django.urls import reverse
from unittest.mock import patch, Mock
from general.models import RecentlyViewed
import json


class TVshowModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='password123')

        self.show = TVshow.objects.create(
            user=self.user,
            show_id=1,
            title="Test Show",
            first_air_date="2022",
            description="This is a test show.",
            poster_url="http://example.com/poster.jpg",
            status="currently_watching",
        )

    def test_tvshow_creation(self):
        tvshow = TVshow.objects.get(show_id=1)
        self.assertEqual(tvshow.title, "Test Show")
        self.assertEqual(tvshow.first_air_date, "2022")
        self.assertEqual(tvshow.status, "currently_watching")
        self.assertEqual(tvshow.user.username, "testuser")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            TVshow.objects.create(
                user=self.user,
                show_id=1,
                title="Duplicate Show",
                first_air_date="2023",
                status="watch_later"
            )

    def test_default_status(self):
        tvshow = TVshow.objects.create(
            user=self.user,
            show_id=2,
            title="Another Show",
            first_air_date="2023"
        )
        self.assertEqual(tvshow.status, "watch_later")

    def test_str_method(self):
        tvshow = self.show
        self.assertEqual(str(tvshow), "Test Show (2022) - testuser")

    def test_last_updated_auto_now(self):

        tvshow = self.show
        original_last_updated = tvshow.last_updated
        tvshow.save()
        self.assertNotEqual(tvshow.last_updated, original_last_updated)

    def test_added_at_default(self):

        tvshow = self.show
        self.assertEqual(tvshow.added_at.date(), timezone.now().date())

class TVshowSearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        RecentlyViewed.objects.create(
            user=self.user,
            content_type='show',
            item_id=1,
            viewed_at='2025-02-11T12:00:00Z'
        )

    @patch('requests.get')
    @patch.dict('os.environ', {'SHOW_API_KEY': 'TEST_API_KEY'})
    def test_tvshow_search_with_results(self, mock_get):

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{'id': 1, 'name': 'Test Show', 'release_date': '2023-01-01'}]
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('TVshow_search'), {'query': 'Test Show'})

        mock_get.assert_called_with(
            'https://api.themoviedb.org/3/search/tv?query=Test Show&api_key=TEST_API_KEY&language=en-US'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Show')


    @patch('requests.get')
    @patch.dict('os.environ', {'SHOW_API_KEY': 'TEST_API_KEY'})
    def test_tvshow_search_with_no_results(self, mock_get):

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response

        response = self.client.get(reverse('TVshow_search'), {'query': 'Nonexistent Show'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No results found')

    @patch('requests.get')
    @patch.dict('os.environ', {'SHOW_API_KEY': 'TEST_API_KEY'})
    def test_tvshow_search_api_error(self, mock_get):

        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = self.client.get(reverse('TVshow_search'), {'query': 'Test Show'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Error')

class ShowDetailTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.show = TVshow.objects.create(
            user=self.user,
            show_id=1,
            title='Test Show',
            first_air_date='2025',
            description='Description of the show',
            poster_url='http://example.com/poster.jpg'
        )

    def test_show_detail_found_in_db(self):
        response = self.client.get(reverse('show_detail', args=[self.show.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Show')
        self.assertContains(response, 'Description of the show')
        self.assertContains(response, 'http://example.com/poster.jpg')
    @patch('TVshow.views.get_tv_show_from_api')
    def test_show_detail_not_found_in_db(self, mock_get_tv_show_from_api):
        mock_api_data = {
            'id': 2,
            'name': 'API Show',
            'first_air_date': '2026',
            'overview': 'API show description',
            'poster_path': '/poster.jpg'
        }
        mock_get_tv_show_from_api.return_value = mock_api_data

        response = self.client.get(reverse('show_detail', args=[2]))  

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Show')
        self.assertContains(response, 'API show description')
        self.assertContains(response, 'https://image.tmdb.org/t/p/w500/poster.jpg') 

    @patch('TVshow.views.get_tv_show_from_api')
    def test_show_detail_api_error(self, mock_get_tv_show_from_api):
        mock_get_tv_show_from_api.return_value = None

        self.show_detail_url = lambda show_id: reverse('show_detail', kwargs={'show_id': show_id})
        response = self.client.get(self.show_detail_url(789))


        self.assertEqual(response.status_code, 404)

    @patch('TVshow.views.add_to_recently_viewed')
    @patch('myapp.views.get_tv_show_from_api')
    def test_add_to_recently_viewed(self, mock_get_tv_show_from_api, mock_add_to_recently_viewed):
        mock_api_data = {
            'id': 2,
            'name': 'API Show',
            'first_air_date': '2026',
            'overview': 'API show description',
            'poster_path': '/poster.jpg'
        }
        mock_get_tv_show_from_api.return_value = mock_api_data

        self.client.get(reverse('show_detail', args=[2])) 

        mock_add_to_recently_viewed.assert_called_with(
            self.user,
            'show',
            2,
            'API Show',
            'https://image.tmdb.org/t/p/w500/poster.jpg'
        )

class AddOrUpdateShowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_add_show_success(self):
        url = reverse('add_or_update_show')  
        data = {
            'show_id': 1,
            'title': 'Test Show',
            'first_air_date': '2022',
            'description': 'Description of the show',
            'poster_url': 'http://example.com/poster.jpg',
            'status': 'watch_later'
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'message': 'TV Show added or updated successfully',
            'status': 'watch_later'
        })

        show = TVshow.objects.get(show_id=1)
        self.assertEqual(show.title, 'Test Show')
        self.assertEqual(show.status, 'watch_later')

    def test_update_show_status(self):

        TVshow.objects.create(
            user=self.user,
            show_id=1,
            title='Test Show',
            first_air_date='2022',
            description='Description of the show',
            poster_url='http://example.com/poster.jpg',
            status='watch_later'
        )
        
        url = reverse('add_or_update_show')  
        data = {
            'show_id': 1,
            'title': 'Test Show Updated',
            'first_air_date': '2023',
            'description': 'Updated description',
            'poster_url': 'http://example.com/updated_poster.jpg',
            'status': 'currently_watching'
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'message': 'TV Show added or updated successfully',
            'status': 'currently_watching'
        })
        
        show = TVshow.objects.get(show_id=1)
        self.assertEqual(show.status, 'currently_watching')

    def test_invalid_show_id(self):
        url = reverse('add_or_update_show')  
        data = {
            'show_id': 'invalid_id', 
            'title': 'Test Show',
            'first_air_date': '2022',
            'description': 'Description of the show',
            'poster_url': 'http://example.com/poster.jpg',
            'status': 'watch_later'
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Valid show ID is required"})
    def test_invalid_json(self):
        url = reverse('add_or_update_show') 
        data = 'invalid_json' 

        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid JSON data'})

    @patch('TVshow.views.TVshow.objects.get_or_create')
    def test_server_error(self, mock_get_or_create):
        mock_get_or_create.side_effect = Exception('Something went wrong')

        url = reverse('add_or_update_show')
        data = {
            'show_id': 1,
            'title': 'Test Show',
            'first_air_date': '2022',
            'description': 'Description of the show',
            'poster_url': 'http://example.com/poster.jpg',
            'status': 'watch_later'
        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {'error': 'Something went wrong'})

class ShowMainTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        self.show1 = TVshow.objects.create(
            user=self.user,
            show_id=1,
            title="Test Show 2",
            first_air_date="2022",
            description="Description 1",
            poster_url="http://example.com/poster1.jpg",
            status="watch_later"
        )
        self.show2 = TVshow.objects.create(
            user=self.user,
            show_id=2,
            title="Test Show 1",
            first_air_date="2023",
            description="Description 2",
            poster_url="http://example.com/poster2.jpg",
            status="currently_watching"
        )

    def test_show_main_no_filters(self):
        url = reverse('show_main')  
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        tvshows = list(response.context['tvshows'])

        self.assertEqual(
            [show.show_id for show in tvshows],
            [self.show1.show_id, self.show2.show_id]
        )

    def test_show_main_with_status_filter(self):
        url = reverse('show_main') + '?status=watch_later'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        tvshows = list(response.context['tvshows'])
        tvshows_filtered = [tvshow for tvshow in tvshows if tvshow.status == 'watch_later']
        self.assertEqual(
            [show.show_id for show in tvshows],
            [self.show1.show_id]
        )
    def test_show_main_sorted_by_title(self):
        url = reverse('show_main') + '?sort_by=title'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        tvshows = list(response.context['tvshows'])
        tvshows_sorted = sorted(tvshows, key=lambda x: x.title)

        self.assertEqual(
            [show.show_id for show in tvshows],
            [self.show2.show_id, self.show1.show_id]
        )

    def test_show_main_sorted_by_date(self):
        url = reverse('show_main') + '?sort_by=date'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        tvshows = list(response.context['tvshows'])
        tvshows_sorted = sorted(tvshows, key=lambda x: x.last_updated, reverse=True)

        self.assertEqual(
            [show.show_id for show in tvshows],
            [self.show2.show_id, self.show1.show_id]
        )

class DeleteShowTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        self.show = TVshow.objects.create(
            user=self.user,
            show_id=1,
            title="Test Show",
            first_air_date="2022",
            description="Description",
            poster_url="http://example.com/poster.jpg",
            status="watch_later"
        )

    def test_delete_show_success(self):
 
        initial_count = TVshow.objects.count()

        url = reverse('delete_show', args=[self.show.show_id])  
        response = self.client.delete(url)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Show deleted successfully')


        self.assertEqual(TVshow.objects.count(), initial_count - 1)

    def test_delete_show_not_found(self):

        url = reverse('delete_show', args=[999]) 
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Failed to delete show: Show matching query does not exist.')

    def test_delete_show_invalid_method(self):

        url = reverse('delete_show', args=[self.show.show_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid request method')

    @patch('TVshow.views.get_object_or_404')
    def test_delete_show_server_error(self, mock_get_object):

        mock_get_object.side_effect = Exception("Test exception")

        url = reverse('delete_show', args=[self.show.show_id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error'], 'Failed to delete show: Test exception')






