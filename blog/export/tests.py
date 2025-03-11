# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ProfileTemplateTests(TestCase):
    def setUp(self):
        # Create a staff user (since staff URL references are what we're testing)
        self.staff_user = User.objects.create_user(
            username="staffuser", password="testpassword", is_staff=True
        )

    def test_profile_page_loads_for_staff_user(self):
        """Test that management page loads without errors for staff users"""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("blog:management:data-console"))

        # Check the page loads successfully
        self.assertEqual(response.status_code, 200)

    # TODO: add more functional unit tests
