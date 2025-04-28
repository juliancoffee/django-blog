from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from blog.models import Post, Comment
from blog.notifications.models import Subscription

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='test@example.com'
)
class NotificationEmailTests(TestCase):
    """Test email notifications sent when posts are created or updated."""

    def setUp(self):
        # Create an author
        self.author = User.objects.create_user(
            username='author', email='author@example.com', password='password123'
        )

        # New-post subscribers
        self.new_post_subscriber1 = User.objects.create_user(
            username='new_sub1', email='newsub1@example.com', password='password123'
        )
        self.new_post_subscriber2 = User.objects.create_user(
            username='new_sub2', email='newsub2@example.com', password='password123'
        )

        # Engaged-post subscriber (will comment)
        self.engaged_subscriber = User.objects.create_user(
            username='engaged_sub', email='engagedsub@example.com', password='password123'
        )

        # Non-subscriber for control
        self.non_subscriber = User.objects.create_user(
            username='nonsub', email='nonsub@example.com', password='password123'
        )

        # Create subscription records
        Subscription.objects.create(user=self.new_post_subscriber1, to_new_posts=True, to_engaged_posts=False)
        Subscription.objects.create(user=self.new_post_subscriber2, to_new_posts=True, to_engaged_posts=False)
        Subscription.objects.create(user=self.engaged_subscriber, to_new_posts=False, to_engaged_posts=True)

        # Create an existing post
        self.existing_post = Post.objects.create(
            title="Existing Post",
            text="This is an existing post for testing updates",
            pub_date=timezone.now(),
            author=self.author
        )

        # Add a comment from the engaged subscriber
        Comment.objects.create(
            post=self.existing_post,
            author=self.engaged_subscriber,
            text="This is a comment from an engaged subscriber",
            pub_date=timezone.now()
        )

        # Clear any sent emails
        mail.outbox = []

    def test_new_post_notification(self):
        """New post creation sends emails to new-post subscribers only."""
        # Create a fresh post
        post = Post.objects.create(
            title="New Test Post",
            text="This is a new post that should trigger notifications",
            pub_date=timezone.now(),
            author=self.author
        )

        # Two emails should be sent
        self.assertEqual(len(mail.outbox), 2)
        recipients = {msg.to[0] for msg in mail.outbox}

        # Verify correct recipients
        self.assertIn(self.new_post_subscriber1.email, recipients)
        self.assertIn(self.new_post_subscriber2.email, recipients)
        self.assertNotIn(self.non_subscriber.email, recipients)
        self.assertNotIn(self.engaged_subscriber.email, recipients)

        # Verify email content and subject
        for msg in mail.outbox:
            self.assertEqual(msg.subject, "Such Subject")
            self.assertIn(post.text[:30], msg.body)

    def test_updated_post_notification(self):
        """Updating an existing post sends emails to both new-post and engaged-post subscribers."""
        mail.outbox = []

        # Update text on the existing post
        self.existing_post.text = "This post has been updated and should trigger notifications"
        self.existing_post.save()

        # Expect 3 emails: 2 new-post + 1 engaged-post
        self.assertEqual(len(mail.outbox), 3)
        recipients = {msg.to[0] for msg in mail.outbox}

        self.assertIn(self.new_post_subscriber1.email, recipients)
        self.assertIn(self.new_post_subscriber2.email, recipients)
        self.assertIn(self.engaged_subscriber.email, recipients)
        self.assertNotIn(self.non_subscriber.email, recipients)

        for msg in mail.outbox:
            self.assertEqual(msg.subject, "Such Subject")
            self.assertIn(self.existing_post.text[:30], msg.body)

    def test_delayed_post_notification(self):
        """Posts with future pub_date don't send emails until they are published."""
        mail.outbox = []

        # Create a future-dated post
        future_date = timezone.now() + timedelta(days=1)
        post = Post.objects.create(
            title="Future Post",
            text="This is a post with a future publication date",
            pub_date=future_date,
            author=self.author
        )

        # No emails should be sent initially
        self.assertEqual(len(mail.outbox), 0)

        # Simulate publication now
        post.pub_date = timezone.now()
        post.save()

        # Now 2 emails to new-post subscribers
        self.assertEqual(len(mail.outbox), 2)
