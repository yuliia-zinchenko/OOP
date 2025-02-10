from django.test import TestCase
from django.contrib.auth.models import User
from .models import Movie
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

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



