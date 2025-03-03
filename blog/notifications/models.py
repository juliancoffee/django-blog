# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class NewPostSubscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user


class EngagedPostSubscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user
