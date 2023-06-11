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


class Indicator(models.Model):
    INDICATOR_CHOICES = (
        ('GLOBAL', 'Global Indicator'),
        ('INDIAN', 'Indian Indicator'),
        ('TOPGAINER', 'Top Gainer'),
        ('TOPLOSER', 'Top Loser'),
        ('TOPCRYPTO', 'Top Crypto'),
    )
    
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2)
    percentage_change = models.DecimalField(max_digits=6, decimal_places=2)
    indicator_type = models.CharField(max_length=10, choices=INDICATOR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
