#
# THIS WHOLE FILE WAS GENERATED BY CodeRabbitAI
#
# well, almost
#
import logging

from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from blog.models import Post

from .forms import SubscribeForm
from .models import Subscription

logging.disable()


class SubscriptionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

    def test_subscription_creation(self):
        """Test that a Subscription instance can be created"""
        subscription = Subscription.objects.create(
            user=self.user, to_new_posts=True, to_engaged_posts=False
        )
        self.assertEqual(subscription.user, self.user)
        self.assertTrue(subscription.to_new_posts)
        self.assertFalse(subscription.to_engaged_posts)

    def test_subscription_string_representation(self):
        """Test that the string representation is correct"""
        subscription = Subscription.objects.create(
            user=self.user, to_new_posts=True, to_engaged_posts=False
        )
        expected_str = "For testuser"
        self.assertEqual(str(subscription), expected_str)

    def test_subscription_default_values(self):
        """Test that default values are set correctly"""
        subscription = Subscription.objects.create(user=self.user)
        self.assertFalse(subscription.to_new_posts)
        self.assertFalse(subscription.to_engaged_posts)


class SubscribeFormTests(TestCase):
    def test_form_valid_data(self):
        """Test that the form validates with correct data"""
        form_data = {"to_new_posts": True, "to_engaged_posts": True}
        form = SubscribeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_empty_data(self):
        """Test that the form is valid even without data (as fields are not required)"""
        form = SubscribeForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_field_labels(self):
        """Test that the form fields have the correct labels"""
        form = SubscribeForm()
        self.assertEqual(
            form.fields["to_new_posts"].label, "Subscribe to new posts"
        )
        self.assertEqual(
            form.fields["to_engaged_posts"].label,
            "Subscribe to updates on engaged posts",
        )


class NotificationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.settings_url = reverse("blog:notifications:settings")

    def test_settings_view_get_authenticated(self):
        """Test that authenticated users can access the settings page"""
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/notif_settings.html")
        self.assertIsInstance(response.context["form"], SubscribeForm)

    def test_settings_view_post_valid_data(self):
        """Test that users can update their subscription preferences"""
        self.client.login(username="testuser", password="testpassword")

        # Initially there should be no subscription
        self.assertEqual(Subscription.objects.count(), 0)

        # Submit the form
        response = self.client.post(
            self.settings_url, {"to_new_posts": True, "to_engaged_posts": False}
        )

        # Should redirect to settings page after successful update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.settings_url)

        # Check that subscription was created with correct values
        self.assertEqual(Subscription.objects.count(), 1)
        subscription = Subscription.objects.get(user=self.user)
        self.assertTrue(subscription.to_new_posts)
        self.assertFalse(subscription.to_engaged_posts)

    def test_settings_view_post_update_existing(self):
        """Test that an existing subscription can be updated"""
        self.client.login(username="testuser", password="testpassword")

        # Create an initial subscription
        subscription = Subscription.objects.create(
            user=self.user, to_new_posts=False, to_engaged_posts=False
        )

        # Update via form submission
        self.client.post(
            self.settings_url, {"to_new_posts": True, "to_engaged_posts": True}
        )

        # Check that values were updated
        subscription.refresh_from_db()
        self.assertTrue(subscription.to_new_posts)
        self.assertTrue(subscription.to_engaged_posts)

    def test_get_or_create_subscription(self):
        """Test that get_or_create works properly for retrieving or creating subscriptions"""
        self.client.login(username="testuser", password="testpassword")

        # We shouldn't have any subscriptions at the beginning
        self.assertEqual(Subscription.objects.count(), 0)

        # First access should create a new subscription
        _ = self.client.get(self.settings_url)
        self.assertEqual(Subscription.objects.count(), 1)

        # Subsequent access should use the same subscription
        _ = self.client.get(self.settings_url)
        self.assertEqual(Subscription.objects.count(), 1)

    def test_subscription_cascade_deletion(self):
        """Test that subscriptions are deleted when the associated user is deleted"""
        # Create a user and subscription
        user = User.objects.create_user(
            username="tempuser", password="temppass"
        )
        subscription = Subscription.objects.create(
            user=user, to_new_posts=True, to_engaged_posts=True
        )

        # Verify subscription exists
        self.assertEqual(Subscription.objects.filter(user=user).count(), 1)

        # Delete the user
        user.delete()

        # Verify the subscription was also deleted
        self.assertEqual(
            Subscription.objects.filter(id=subscription.id).count(), 0
        )


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

    def test_end_to_end_subscription_workflow(self):
        """
        Test the complete flow:
        1. User logs in
        2. Navigates to settings
        3. Updates preferences
        4. Verifies changes when revisiting the page
        """
        # p. s.
        # Testing forms in Django is kind of annoying.
        # - If you have ModelForm, you need to use `form.instance.<field>`
        # - If it's a regular Form, you need to use `form.data["<field>"]`
        #
        # I like Django forms less and less.
        #
        # p. p. s. coderabbitai made my change my comments, because previous
        # ones were "considered unprofessional"

        self.client.login(username="testuser", password="testpassword")
        settings_url = reverse("blog:notifications:settings")

        # First visit - should show default values (unchecked)
        response = self.client.get(settings_url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.instance.to_new_posts)
        self.assertFalse(form.instance.to_engaged_posts)

        # Update preferences
        response = self.client.post(
            settings_url, {"to_new_posts": True, "to_engaged_posts": True}
        )
        self.assertEqual(response.status_code, 302)

        # Visit again - form should now show checked values
        response = self.client.get(settings_url)
        form = response.context["form"]
        self.assertTrue(form.instance.to_new_posts)
        self.assertTrue(form.instance.to_engaged_posts)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
)
class NotificationEmailTests(TestCase):
    """Test email notifications sent when posts are created or updated."""

    def setUp(self):
        """Set up test data."""
        # Subscribers to new posts
        self.new_post_subscriber1 = User.objects.create_user(
            username="new_sub1",
            email="newsub1@example.com",
            password="password123",
        )
        self.new_post_subscriber2 = User.objects.create_user(
            username="new_sub2",
            email="newsub2@example.com",
            password="password123",
        )

        # Subscribers to engaged posts (needs to have commented)
        self.engaged_subscriber = User.objects.create_user(
            username="engaged_sub",
            email="engagedsub@example.com",
            password="password123",
        )

        # Non-subscriber for control
        self.non_subscriber = User.objects.create_user(
            username="nonsub",
            email="nonsub@example.com",
            password="password123",
        )

        # Create subscriptions
        Subscription.objects.create(
            user=self.new_post_subscriber1,
            to_new_posts=True,
            to_engaged_posts=False,
        )
        Subscription.objects.create(
            user=self.new_post_subscriber2,
            to_new_posts=True,
            to_engaged_posts=False,
        )
        Subscription.objects.create(
            user=self.engaged_subscriber,
            to_new_posts=False,
            to_engaged_posts=True,
        )

        # Clear the email outbox before each test
        mail.outbox = []

    def test_new_post_notification(self):
        """Test that new post notifications are sent"""
        # Create a new post
        post = Post.objects.create(
            post_text="This is a new post that should trigger notifications",
            pub_date=timezone.now(),
        )

        # Check that emails were sent, one for each subscriber
        self.assertEqual(len(mail.outbox), 2)

        # Get the recipient emails from the sent messages
        recipient_emails = [msg.to for msg in mail.outbox]

        # Verify that both new post subscribers received emails
        # And it doesn't list other subscribers
        self.assertSequenceEqual(
            sorted(
                [
                    [self.new_post_subscriber1.email],
                    [self.new_post_subscriber2.email],
                ]
            ),
            sorted(recipient_emails),
        )

        # Check email content
        # Check that post text is in the email
        for msg in mail.outbox:
            self.assertEqual(msg.subject, "Such Subject")
            self.assertIn(post.post_text[:30], msg.body)
