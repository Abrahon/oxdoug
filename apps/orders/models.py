from django.db import models
from apps.accounts.models import User
from apps.common.models import TimeStampedModel
from apps.products.models import Products
from apps.coupons.models import Coupon
import secrets
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.orders.enums import PaymentMethod, PaymentStatus, OrderStatus



class Order(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_number = models.CharField(max_length=255, unique=True, editable=False)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )
    shipping_address = models.ForeignKey(
        "checkout.Shipping",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discounted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_paid = models.BooleanField(default=False)

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)


    # order number genarete
    def __str__(self):
        return f"{self.order_number} — {self.user}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            ts = timezone.now().strftime("%Y%m%d%H%M%S")
            rnd = secrets.token_hex(3)
            self.order_number = f"ORD-{ts}-{rnd}"
        super().save(*args, **kwargs)
        

    
    # calculate total ammount 
    def calculate_totals(self):
        """Recalculate totals from items + coupon"""
        subtotal = sum(item.line_total for item in self.items.all())
        self.total_amount = subtotal

        if self.coupon:
            discount = (subtotal * self.coupon.discount_percentage) / Decimal("100.0")
            self.discount_amount = discount
            self.final_amount = subtotal - discount
        else:
            self.discount_amount = Decimal("0.00")
            self.final_amount = subtotal
        return self.final_amount




class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    @property
    def line_total(self):
        return (self.price or Decimal("0.00")) * self.quantity
