from django.db import models
from cloudinary.models import CloudinaryField

class HeroPromotion(models.Model):
    title1 = models.CharField(max_length=255)
    title2 = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title1





class HeroPromotionImage(models.Model):
    hero_promotion = models.ForeignKey(
        HeroPromotion,
        related_name='images',
        on_delete=models.CASCADE
    )

    image = CloudinaryField('image', blank=True, null=True)

    heading = models.CharField(max_length=255, blank=True, null=True)
    sub_heading = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.heading or 'Image'} - {self.hero_promotion.title1}"
