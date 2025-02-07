from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserBook
from django.urls import reverse

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

    def test_index_view_no_query(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('books', response.context)
        self.assertIn('movies', response.context)









