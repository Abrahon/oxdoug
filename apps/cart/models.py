# from django.db import models

# from django.db import models
# from django.conf import settings
# from apps.products.models import Products


# User = settings.AUTH_USER_MODEL

# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
#     product = models.ForeignKey(Products, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ['user', 'product']
#         ordering = ['-added_at']

#     def __str__(self):
#         return f"{self.user} - {self.product.title} ({self.quantity})"

# from django.db import models
# from django.conf import settings
# from apps.products.models import Products

# User = settings.AUTH_USER_MODEL


# class CartItem(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="cart_items",
#         null=True,
#         blank=True
#     )

#     session_key = models.CharField(
#         max_length=255,
#         null=True,
#         blank=True
#     )

#     product = models.ForeignKey(
#         Products,
#         on_delete=models.CASCADE
#     )

#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-added_at"]

#     def __str__(self):
#         owner = self.user if self.user else self.session_key
#         return f"{owner} - {self.product.title} ({self.quantity})"

from django.db import models
from django.conf import settings
from apps.products.models import Products

User = settings.AUTH_USER_MODEL

class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key}"
        return f"{owner} - {self.product.title} ({self.quantity})"

    class Meta:
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product"
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"], name="unique_session_product"
            ),
        ]