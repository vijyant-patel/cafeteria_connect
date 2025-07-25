from django.db import models
from core.models import User

class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    floor = models.IntegerField()
    contact = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.name} - {self.shop.name}"
