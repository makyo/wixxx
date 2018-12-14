from django.contrib.auth.models import User
from django.db import models


class Flag(models.Model):

    flag = models.TextField(unique=True)

    class Meta:

        indexes = ['flag']


class Character(models.Model):

    name = models.TextField(unique=True)
    flags = models.ManyToManyField(Flag)

    class Meta:
        
        indexes = ['name']


class Token(models.Model):

    token = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class UserSecret(models.Model):

    secret = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
