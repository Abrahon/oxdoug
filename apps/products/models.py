import os
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel

class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

def product_image_path(instance, filename):
    base, ext = os.path.splitext(filename)
    slug = slugify(instance.title)
    return f'product_images/{slug}-{os.urandom(4).hex()}{ext}'

def product_video_path(instance, filename):
    """
    Custom path for uploaded product videos
    """
    base, ext = os.path.splitext(filename)
    slug = slugify(instance.title)
    return f'product_videos/{slug}-{os.urandom(4).hex()}{ext}'


class Products(TimeStampedModel):
    title = models.CharField(max_length=255)
    avg_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0
    )
    product_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    colors = models.JSONField(default=list)
    available_stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    discount = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage (0-100)"
    )
    main_image = models.URLField(blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)

    features = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate product_code only once
        if not self.product_code:
            import uuid
            self.product_code = f"PRD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    @property
    def discounted_price(self):
        """
        Calculate price after discount
        """
        if self.discount and self.discount > 0:
            return round(float(self.price) * (1 - self.discount / 100), 2)
        return float(self.price)
