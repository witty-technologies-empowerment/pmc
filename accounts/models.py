from django.db import models
from django.contrib.auth.models import User


class userContact(models.Model):
    user = models.CharField(max_length=20)
    telephone = models.CharField(max_length=12)

    def __str__(self):
        return self.user + " telephone is " + self.telephone + "."