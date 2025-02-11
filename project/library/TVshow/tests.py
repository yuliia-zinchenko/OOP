from django.test import TestCase
from django.contrib.auth.models import User
from .models import TVshow
from django.utils import timezone

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

