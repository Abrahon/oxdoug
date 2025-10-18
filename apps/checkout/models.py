# b2c/checkout/models.py
from django.db import models
from apps.accounts.models import User
from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Shipping(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shippings')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shippings', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=20)
    email = models.EmailField()
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    floor = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
    

