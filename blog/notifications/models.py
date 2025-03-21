# Create your models here.
from django.contrib.auth.models import User
from django.db import models


# We technically could use multiple tables per each subscription type, but
# having one table makes it simply so much easier.
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    to_new_posts = models.BooleanField(default=False)
    to_engaged_posts = models.BooleanField(default=False)

    def __str__(self):
        return f"For {self.user.username}"
