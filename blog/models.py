from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable
from typing import override

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.db import models
from django.utils import timezone

from blog.notifications.models import Subscription

from .utils import MAX_COMMENT_LENGTH

logger = logging.getLogger(__name__)


TEXT_CROP_LEN = 30


def subscriber_emails(post: Post) -> Iterable[str]:
    """
    Returns a list of people subscribed to the post
    """

    # fetch everyone who is subscribed to new posts
    # WARN: we don't filter new posts vs updates to posts
    because_new = (
        Subscription.objects.filter(to_new_posts=True)
        .select_related("user")
        .values_list("user")
    )

    # fetch the intersection of:
    # - users with engaged_posts enabled
    # - users who commented on that post
    query_subscribers = Subscription.objects.filter(
        to_engaged_posts=True
    ).values_list("user")
    # WARN: we don't filter whether the update is because of subscriber
    # comment
    query_commenters = Comment.objects.filter(post_id=post.id).values_list(
        "commenter"
    )
    because_engaged = query_subscribers.intersection(query_commenters)

    # get emails
    subscribers = because_new.union(because_engaged)

    # NOTE: this whole function is one single DB query, yay
    return User.objects.filter(id__in=subscribers).values_list(
        "email", flat=True
    )


def send_notifications_to(
    emails_to: Iterable[str], post_text: str, date: datetime.datetime
):
    """
    Sends post notifications
    """

    if not emails_to:
        logger.info("No users to send notifications to.")
        return

    if len(post_text) < TEXT_CROP_LEN:
        text = post_text
    else:
        text = f"{post_text[:TEXT_CROP_LEN]}..."

    # NOTE: use send_mass_mail here and not a send_mail to send multiple emails
    # with each having their own target
    send_mass_mail(
        map(
            lambda email: (
                "Such Subject",
                f"Hi check out our post update!\n{date}\n{text}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            ),
            emails_to,
        )
    )


class Post(models.Model):
    post_text = models.CharField(max_length=500)
    pub_date = models.DateTimeField("publishing date")

    @override
    def __str__(self) -> str:
        return self.post_text

    @override
    def save(self, *args, **kwargs) -> None:
        # call default impl
        super().save(*args, **kwargs)

        # hook notifications in
        self.send_notifications()

    def send_notifications(self) -> None:
        post_text = self.post_text
        pub_date = self.pub_date

        if pub_date > timezone.now():
            # FIXME: delayed posts won't receive any notifications
            #
            # not sure how to fix it without some complicated machinery
            pass

        emails_to = subscriber_emails(self)
        send_notifications_to(emails_to, post_text, pub_date)

    def was_published_recently(self) -> bool:
        # this is a stupid method, but Django tutorial said that I should
        # add it
        #
        # ... and test it
        if self.pub_date > timezone.now():
            # no timetravelers here, please
            return False

        # one minute because, uhm, time flies
        #
        # so like, if we have a post that was published exactly day ago, by the
        # time Python goes to evaluate this expression, some seconds have passed
        # and this breaks tests
        #
        # shouldn't we fix the tests instead? well, maybe ...
        # but idk
        return timezone.now() - self.pub_date < datetime.timedelta(
            days=1, minutes=1
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=MAX_COMMENT_LENGTH)
    pub_date = models.DateTimeField("publishing date")

    # blank=True to mark as optional in Django Admin
    commenter_ip = models.GenericIPAddressField(null=True, blank=True)
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @override
    def __str__(self) -> str:
        return self.comment_text
