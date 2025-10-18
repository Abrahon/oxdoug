

from django.db import models

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    DELIVERD = 'success', 'Deliverd'
    CANCELL = 'cancelled', 'Cancelled',

class PaymentMethod(models.TextChoices):
    COD = "COD", "Cash on Delivery"
    ONLINE = "ONLINE", "Online Payment"




class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"



