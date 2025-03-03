# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class PostSubscribers:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
