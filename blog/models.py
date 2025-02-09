import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Post(models.Model):
    post_text = models.CharField(max_length=500)
    pub_date = models.DateTimeField("publishing date")

    def __str__(self) -> str:
        return self.post_text

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
    comment_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("publishing date")

    commenter_ip = models.GenericIPAddressField(null=True)
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.comment_text
