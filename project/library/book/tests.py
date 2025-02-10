from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserBook
from django.urls import reverse
from general.models import Quote
from movie.models import Movie
from TVshow.models import TVshow
from book.forms import BookSearchForm
import responses
from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from datetime import datetime, timedelta
from general.models import RecentlyViewed
import json
from django.utils.timezone import now
from django.http import JsonResponse


class UserBookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
    
    def test_create_userbook(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Test Book",
            author="Test Author",
            genre="Fiction",
            status="read_later",
            cover_image_url="http://example.com/image.jpg"
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.genre, "Fiction")
        self.assertEqual(book.status, "read_later")
        self.assertEqual(book.cover_image_url, "http://example.com/image.jpg")
        self.assertTrue(isinstance(book, UserBook))
        self.assertEqual(str(book), 'Test Book by Test Author')
    def test_unique_user_and_book_id(self):
        book1 = UserBook.objects.create(
            user=self.user,
            title="Test Book",
            genre="Fiction",
            status="read_later"
        )
        with self.assertRaises(Exception):  
            book2 = UserBook.objects.create(
                user=self.user,
                title="Another Test Book",
                genre="Fiction",
                book_id=book1.book_id,
                status="currently_reading"
            )
    def test_book_id_generation(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Generated Book",
            genre="Fiction",
            status="read_later"
        )
        self.assertTrue(book.book_id.startswith("user-"))
    def test_title_and_genre_truncation(self):
        long_title = "A" * 100 
        long_genre = "B" * 300 
        book = UserBook.objects.create(
            user=self.user,
            title=long_title,
            genre=long_genre,
            status="read_later"
        )
        self.assertEqual(len(book.title), 50)
        self.assertEqual(len(book.genre), 250)
    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            UserBook.objects.create(
                user=self.user,
                title="Invalid Status Book",
                genre="Fiction",
                status="invalid_status",
            )
    def test_timestamps(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Timestamp Book",
            genre="Fiction",
            status="read_later"
        )
        self.assertIsNotNone(book.added_at)
        self.assertIsNotNone(book.last_updated)
    def test_last_updated_field(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Original Title",
            genre="Fiction",
            status="read_later"
        )
        old_last_updated = book.last_updated
        book.title = "Updated Title"
        book.save()
        self.assertNotEqual(book.last_updated, old_last_updated)
    def test_same_book_with_different_status(self):
        book1 = UserBook.objects.create(
            user=self.user,
            title="Test Book",
            author="Test Author",
            genre="Fiction",
            status="read_later"
        )
        book2 = UserBook.objects.create(
            user=self.user,
            title="Test Book",
            author="Test Author",
            genre="Fiction",
            status="currently_reading"
        )
        self.assertNotEqual(book1.id, book2.id)  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def test_cover_image_url_optional(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Test Book Without Cover",
            genre="Fiction",
            status="read_later",
            cover_image_url=None
        )
        self.assertIsNone(book.cover_image_url)

        book2 = UserBook.objects.create(
            user=self.user,
            title="Test Book Without Cover Again",
            genre="Fiction",
            status="read_later",
            cover_image_url=""
        )
        self.assertEqual(book2.cover_image_url, "")
    def test_unique_book_id_across_users(self):
        user2 = User.objects.create_user(username="seconduser", password="password")
        book1 = UserBook.objects.create(
            user=self.user,
            title="Shared Book",
            genre="Fiction",
            status="read_later"
        )
        book2 = UserBook.objects.create(
            user=user2,
            title="Shared Book",
            genre="Fiction",
            status="read_later"
        )
        self.assertNotEqual(book1.book_id, book2.book_id)
    def test_delete_user_cascade(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Test Book",
            genre="Fiction",
            status="read_later"
        )
        self.user.delete()
        self.assertEqual(UserBook.objects.filter(id=book.id).count(), 0)
    def test_unique_together_constraint(self):
        book1 = UserBook.objects.create(
            user=self.user,
            title="Unique Together Book",
            genre="Fiction",
            status="read_later"
        )
        with self.assertRaises(Exception):
            UserBook.objects.create(
                user=self.user,
                title="Unique Together Book",
                genre="Fiction",
                book_id=book1.book_id,
                status="currently_reading"
            )
    def test_create_book_without_author(self):
        book = UserBook.objects.create(
            user=self.user,
            title="Authorless Book",
            status="read_later"
        )
        self.assertIsNone(book.author)
        self.assertIsNone(book.genre)

class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.url = reverse('book_main') 

    def test_index_view_accessible_to_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_redirects_for_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(''))
    def test_quote_of_the_day(self):
        Quote.objects.create(text="Test Quote 1")
        Quote.objects.create(text="Test Quote 2")

        response = self.client.get(self.url)
        self.assertIn('quote', response.context)
        self.assertIsNotNone(response.context['quote'])

    def test_search_functionality(self):
        UserBook.objects.create(user=self.user, title="Test Book", author="Author 1", status="read_later")
        Movie.objects.create(user=self.user, title="Test Movie", release_year="2023", status="watch_later", movie_id="12315")
        TVshow.objects.create(user=self.user, title="Test Show", first_air_date="2023-01-01", status="watch_later", show_id="1234")

        response = self.client.get(self.url, {'q': 'Test'})
        self.assertContains(response, "Test Book")
        self.assertContains(response, "Test Movie")
        self.assertContains(response, "Test Show")
    def test_sort_books_by_title(self):
        UserBook.objects.create(user=self.user, title="ABook", author="Author 2", status="read_later")
        UserBook.objects.create(user=self.user, title="ABooks", author="Author 1", status="read_later")

        response = self.client.get(self.url, {'sort_by': 'title'})
        books = response.context['books']
        self.assertEqual(list(books.values_list('title', flat=True)), ["ABook", "ABooks"])
    def test_sort_books_by_author(self):
        UserBook.objects.create(user=self.user, title="ABook", author="Author 2", status="read_later")
        UserBook.objects.create(user=self.user, title="ABooks", author="Author 1", status="read_later")

        response = self.client.get(self.url, {'sort_by': 'author'})
        books = response.context['books']
        self.assertEqual(list(books.values_list('title', flat=True)), ["ABooks", "ABook"])
    def test_filter_books_by_status(self):
        UserBook.objects.create(user=self.user, title="Book 1", status="read_later")
        UserBook.objects.create(user=self.user, title="Book 2", status="mark_as_read")

        response = self.client.get(self.url, {'status': 'read_later'})
        books = response.context['books']
        self.assertEqual(books.count(), 1)
        self.assertEqual(books.first().title, "Book 1")

class BookSearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('book_search')

    def test_book_search_form_valid(self):
        data = {'query': 'Text', 'search_by': 'intitle'}
        form = BookSearchForm(data)
        self.assertTrue(form.is_valid())  
        self.assertEqual(form.cleaned_data['query'], 'Text')  
        self.assertEqual(form.cleaned_data['search_by'], 'intitle')

    def test_book_search_form_invalid(self):
        data = {'query': '', 'search_by': 'intitle'}
        form = BookSearchForm(data)
        self.assertFalse(form.is_valid())

    @responses.activate
    def test_search_books_successful_response(self):
        responses.add(
            responses.GET,
            'https://www.googleapis.com/books/v1/volumes',
            json={
                'items': [
                    {'id': '123', 'volumeInfo': {'title': 'Python Programming', 'authors': ['Author 1']}},
                    {'id': '443', 'volumeInfo': {'title': 'Django for Beginners', 'authors': ['Author 2']}},
                ]
            },
            status=200,
        )

        response = self.client.get(self.url, {'query': 'Python', 'search_by': 'intitle'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/book_search.html')
        self.assertContains(response, 'Python Programming')
        self.assertContains(response, 'Django for Beginners')


    def test_recently_viewed_books(self):
        RecentlyViewed.objects.create(user=self.user, content_type='book', item_id=1, viewed_at=datetime.now())
        RecentlyViewed.objects.create(user=self.user, content_type='book', item_id=2, viewed_at=datetime.now() - timedelta(days=1))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        recently_viewed = response.context['recently_viewed_books']
        self.assertEqual(len(recently_viewed), 2)
        self.assertGreater(recently_viewed[0].viewed_at, recently_viewed[1].viewed_at)

class BookDetailTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')


        self.book = UserBook.objects.create(user=self.user, title="Test Book", author="Test Author", book_id="user-1", status='read_later')
        self.url = reverse('book_detail', args=[self.book.book_id])
    
    def test_book_detail_from_userbook(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book") 
        self.assertContains(response, "Test Author")  
    
    def test_book_detail_userbook_not_found(self):
        url = reverse('book_detail', args=["user-999"])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) 

    @patch('requests.get')
    def test_book_detail_from_api_success(self, mock_get):
        mock_response = {
            'volumeInfo': {
                'title': 'Test Book API',
                'authors': ['Test Author'],
                'imageLinks': {
                    'thumbnail': 'http://example.com/test_image.jpg'
                }
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get(reverse('book_detail', args=["test-book-id"]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book API')
        self.assertContains(response, 'Test Author')
        self.assertContains(response, 'http://example.com/test_image.jpg')

    @patch('requests.get')
    def test_book_detail_api_not_found(self, mock_get):
        mock_get.return_value.status_code = 404

        response = self.client.get(reverse('book_detail', args=["test-book-id"]))
        
        self.assertEqual(response.status_code, 404)  

class AddToListTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('add_to_list') 

    def test_add_book_successfully(self):
        data = {
            'book_id': '123',
            'title': 'Test Book',
            'author': 'Test Author',
            'status': 'read_later',
            'genre': 'fiction',
            'cover_image_url': 'http://example.com/cover.jpg'
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Book added successfully')


        book = UserBook.objects.get(user=self.user, book_id='user-123')
        self.assertEqual(book.title, 'Test Book')

    def test_update_book_status_successfully(self):
        UserBook.objects.create(
            user=self.user,
            book_id='user-123',
            title='Test Book',
            author='Test Author',
            status='read_later',
            genre='fiction',
            cover_image_url='http://example.com/cover.jpg',
            last_updated=now()
        )

        data = {
            'book_id': '123',
            'title': 'Test Book',
            'author': 'Test Author',
            'status': 'currently_reading', 
            'genre': 'fiction',
            'cover_image_url': 'http://example.com/cover.jpg'
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Book status updated successfully')

        book = UserBook.objects.get(user=self.user, book_id='user-123')
        self.assertEqual(book.status, 'currently_reading')

    def test_unauthorized_access(self):

        self.client.logout()  
        data = {
            'book_id': '123',
            'title': 'Test Book',
            'author': 'Test Author',
            'status': 'read_later',
            'genre': 'fiction',
            'cover_image_url': 'http://example.com/cover.jpg'
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=' + self.url)

class ManualBookAddTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword') 
        self.url = reverse('manual_book_add') 

    def test_add_new_book(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'fiction',
            'status': 'read_later'
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(UserBook.objects.count(), 1) 
        book = UserBook.objects.first()
        self.assertEqual(book.title, 'Test Book') 
        self.assertEqual(book.author, 'Test Author')
        self.assertEqual(book.genre, 'fiction')
        self.assertEqual(book.status, 'read_later')
    def test_update_existing_book(self):
        existing_book = UserBook.objects.create(
            user=self.user,
            title='Test Book',
            author='Test Author',
            genre='fiction',
            status='read_later'
        )

        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'fiction',
            'status': 'currently_reading'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302) 

        existing_book.refresh_from_db() 
        self.assertEqual(existing_book.status, 'currently_reading')
    def test_redirect_on_successful_submission(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'fiction',
            'status': 'read_later'
        }

        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('book_main'))  

class DeleteBookTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        self.book = UserBook.objects.create(
            user=self.user,
            title='Test Book',
            author='Test Author',
            genre='fiction',
            status='read_later',
            book_id='user-1'
        )
        
        self.url = reverse('delete_book', args=[self.book.book_id])

    def test_delete_book_success(self):
        # Перевірка перед видаленням
        self.assertEqual(UserBook.objects.count(), 1)

        # Виконання DELETE запиту
        response = self.client.delete(self.url)

        # Перевірка, що книга видалена
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Book deleted successfully')
        
        # Перевірка, що книга була видалена з бази
        self.assertEqual(UserBook.objects.count(), 0)

    def test_delete_book_not_found(self):
        # Створюємо іншу книгу, яка не належить користувачу
        another_book = UserBook.objects.create(
            user=self.user,
            title='Another Test Book',
            author='Another Test Author',
            genre='fiction',
            status='read_later',
            book_id='user-2'
        )
        
        # Спробуємо видалити неіснуючу книгу
        url = reverse('delete_book', args=['user-999'])
        response = self.client.delete(url)

        # Перевірка, що повертається статус 404 (Not Found)
        self.assertEqual(response.status_code, 404)

    def test_invalid_method(self):
        # Спробуємо зробити GET запит замість DELETE
        response = self.client.get(self.url)

        # Перевірка, що повертається статус 400 (Invalid request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid request')










