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
    hero_promotion = models.ForeignKey(HeroPromotion, related_name='images', on_delete=models.CASCADE)
    images = CloudinaryField('image', blank=True, null=True) 

    def __str__(self):
        return f"Image for {self.hero_promotion.title1}"
