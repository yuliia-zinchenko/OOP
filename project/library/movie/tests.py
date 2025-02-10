from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Movie
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from unittest.mock import patch
from general.models import RecentlyViewed
from django.urls import reverse
import os
from dotenv import load_dotenv

class MovieModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_movie_successfully(self):
        movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021',
            description='This is a test movie.',
            poster_url='http://example.com/poster.jpg',
            status='watch_later'
        )
        self.assertEqual(Movie.objects.count(), 1)
        self.assertEqual(movie.title, 'Test Movie')

    def test_unique_together_constraint(self):
        Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021'
        )
        with self.assertRaises(IntegrityError):
            Movie.objects.create(
                user=self.user,
                movie_id=123,
                title='Another Movie',
                release_year='2022'
            )

    def test_default_values(self):
        movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021'
        )
        self.assertEqual(movie.status, 'watch_later') 
        self.assertIsNotNone(movie.added_at)

    def test_invalid_status_choice(self):
        with self.assertRaises(ValidationError):
            Movie.objects.create(
                user=self.user,
                movie_id=123,
                title='Test Movie',
                release_year='2021',
                status='invalid_status'
            )

    def test_str_representation(self):
        movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021'
        )
        self.assertEqual(str(movie), 'Test Movie (2021) - testuser')

    def test_last_updated_field(self):
        movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021'
        )
        last_updated_initial = movie.last_updated
        movie.title = 'Updated Title'
        movie.save()
        self.assertNotEqual(movie.last_updated, last_updated_initial)

    def test_foreign_key_cascade_delete(self):
        movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title='Test Movie',
            release_year='2021'
        )
        self.user.delete()
        self.assertEqual(Movie.objects.count(), 0)

class MovieSearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('movie_search') 

    @patch('movie.views.requests.get')  
    def test_movie_search_successful(self, mock_get):

        mock_response = {
            'results': [
                {'id': 1, 'title': 'Test Movie 1', 'release_date': '2023-01-01'},
                {'id': 2, 'title': 'Test Movie 2', 'release_date': '2022-01-01'},
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(self.url, {'query': 'Test Movie'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/movie_search.html')

        self.assertIn('results', response.context)
        self.assertEqual(len(response.context['results']), 2)
        self.assertEqual(response.context['results'][0]['title'], 'Test Movie 1')

    def test_recently_viewed_movies_display(self):
        RecentlyViewed.objects.create(user=self.user, content_type='movie', item_id=1)
        RecentlyViewed.objects.create(user=self.user, content_type='movie', item_id=2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn('recently_viewed_movies', response.context)
        self.assertEqual(response.context['recently_viewed_movies'].count(), 2)

    @patch('movie.views.requests.get')
    def test_api_error_handling(self, mock_get):
        mock_get.return_value.status_code = 500

        response = self.client.get(self.url, {'query': 'Test Movie'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/movie_search.html')

        self.assertIn('results', response.context)
        self.assertEqual(len(response.context['results']), 0)

    def test_empty_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie/movie_search.html')

        self.assertIn('results', response.context)
        self.assertEqual(len(response.context['results']), 0)

    def test_unauthenticated_user_redirect(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302) 

class MovieDetailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        self.movie_detail_url = lambda movie_id: reverse('movie_detail', kwargs={'movie_id': movie_id})

        self.movie = Movie.objects.create(
            user=self.user,
            movie_id=123,
            title="Test Movie",
            release_year="2021",
            description="Test description",
            poster_url="https://example.com/poster.jpg"
        )

    @patch('movie.views.get_movie_from_api')
    @patch('movie.views.add_to_recently_viewed')
    def test_movie_in_database(self, mock_add_to_recently_viewed, mock_get_movie_from_api):
        response = self.client.get(self.movie_detail_url(123))

        self.assertEqual(response.status_code, 200)

        mock_get_movie_from_api.assert_not_called()
        self.assertContains(response, "Test Movie")
        self.assertContains(response, "Test description")

    @patch('movie.views.get_movie_from_api')
    @patch('movie.views.add_to_recently_viewed')
    def test_movie_not_in_database_but_in_api(self, mock_add_to_recently_viewed, mock_get_movie_from_api):
        mock_get_movie_from_api.return_value = {
            'id': 456,
            'title': 'API Movie',
            'release_date': '2023-01-01',
            'overview': 'API description',
            'poster_path': '/api_poster.jpg',
        }

        response = self.client.get(self.movie_detail_url(456))

        self.assertEqual(response.status_code, 200)

        mock_get_movie_from_api.assert_called_once_with(456)

        mock_add_to_recently_viewed.assert_called_once_with(
            self.user,
            'movie',
            456,
            'API Movie',
            'https://image.tmdb.org/t/p/w500/api_poster.jpg'
        )

        self.assertContains(response, "API Movie")
        self.assertContains(response, "API description")

    @patch('movie.views.get_movie_from_api')
    def test_movie_not_found_in_api(self, mock_get_movie_from_api):
        mock_get_movie_from_api.return_value = None

        response = self.client.get(self.movie_detail_url(789))


        self.assertEqual(response.status_code, 404)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.movie_detail_url(123))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('', response.url)

