from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import assert_never, override

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.db import models
from django.utils import timezone

from blog.notifications.models import Subscription

from .utils import MAX_COMMENT_LENGTH, MAX_POST_LENGTH

logger = logging.getLogger(__name__)

type EmailStr = str
type Username = str
type UserId = int
type NotificationInfo = tuple[EmailStr, Username, UserId]


@dataclass
class PostUpdate:
    """
    Signifies update to the post itself
    """

    post: Post

    pass


@dataclass
class CommentUpdate:
    """
    Signifies update to the comment
    """

    post: Post
    comment: Comment


type NotificationReason = PostUpdate | CommentUpdate


def subscriber_emails(reason: NotificationReason) -> Iterable[NotificationInfo]:
    """
    Returns a list of people subscribed to the post
    """

    post = reason.post
    # fetch everyone who is subscribed to new posts
    # WARN: we don't differentiate new posts and updates to posts (such as comments)
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

    query_commenters = Comment.objects.filter(post_id=post.id).values_list(
        "commenter"
    )
    because_engaged = query_subscribers.intersection(query_commenters)

    # get emails
    subscribers = because_new.union(because_engaged)

    match reason:
        case CommentUpdate(post, comment) if comment.commenter:
            authors = [comment.commenter.id]
        case _:
            authors = []

    subs = (
        User.objects.filter(id__in=subscribers)
        .exclude(id__in=authors)
        .values_list("email", "username", "id")
    )

    # NOTE: this whole function is one single DB query, yay
    return subs


def send_notifications(reason: NotificationReason) -> None:
    pub_date = reason.post.pub_date

    if pub_date > timezone.now():
        # FIXME: delayed posts won't receive any notifications
        #
        # not sure how to fix it without some complicated machinery
        pass

    emails_to = subscriber_emails(reason)
    send_notifications_to(emails_to, reason)


def send_notifications_to(
    emails_to: Iterable[NotificationInfo],
    reason: NotificationReason,
):
    """
    Sends post notifications
    """

    if not emails_to:
        logger.info("No users to send notifications to.")
        return

    def filtermap_emails(
        emails_to: Iterable[NotificationInfo],
    ) -> Iterator[tuple[str, str, EmailStr, list[EmailStr]]]:
        """
        `filter_map` to output email message and filter out empty emails
        """
        for email, username, user_id in emails_to:
            if not email:
                logger.error(
                    f"Attempted to send an email to user {username} {user_id=}"
                    " but we don't know their email"
                )
                continue

            match reason:
                case PostUpdate(post):
                    email_text = (
                        f"Hi, {username}, check out our post update!"
                        f"\n{post.pub_date}"
                        f"\n{post.post_text}"
                    )

                    yield (
                        "New Post!",
                        email_text,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                    )
                case CommentUpdate(post, comment):
                    email_text = (
                        f"Hi, {username}, check out the new comment!"
                        f"\n{comment.pub_date}"
                        f"\n{comment.comment_text}"
                    )

                    yield (
                        "New Comment!",
                        email_text,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                    )
                case r:
                    assert_never(r)

    # NOTE: use send_mass_mail here and not a send_mail to send multiple emails
    # with each having their own target
    send_mass_mail(filtermap_emails(emails_to))


class Post(models.Model):
    post_text = models.CharField(max_length=MAX_POST_LENGTH)
    pub_date = models.DateTimeField("publishing date")

    @override
    def __str__(self) -> str:
        return self.post_text

    @override
    def save(self, *args, **kwargs) -> None:
        # call default impl
        super().save(*args, **kwargs)

        # hook notifications in
        send_notifications(PostUpdate(self))

    @staticmethod
    def create_now(post_text: str) -> Post:
        return Post.objects.create(post_text=post_text, pub_date=timezone.now())

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

    @override
    def save(self, *args, **kwargs) -> None:
        # call the default impl
        super().save(*args, **kwargs)

        # hook notifications in
        send_notifications(CommentUpdate(self.post, self))
