
from django.db import models
from apps.accounts.models import User
from apps.common.models import TimeStampedModel
from apps.products.models import Product


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

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discounted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))


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


    def __str__(self):
        return f"Order #{self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime("%Y%m%d")
            last_order_count = Order.objects.filter(order_number__startswith=f"ORD{today}").count() + 1
            self.order_number = f"ORD{today}{last_order_count:03d}"
        super().save(*args, **kwargs)




class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    @property
    def subtotal(self):
        """Calculate total price for this item"""
        return self.quantity * self.price_at_time
