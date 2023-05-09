from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class ListedStock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    slug = models.TextField(max_length=200)
    category = models.CharField(max_length=100)
    flag = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class GlobalIndex(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    slug = models.TextField(max_length=200)
    flag = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class IndianIndex(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    slug = models.TextField(max_length=200)
    flag = models.BooleanField(default=False)

    def __str__(self):
        return self.name