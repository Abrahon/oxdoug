from django.db import models
from cloudinary.models import CloudinaryField

class WhyChooseSection(models.Model):
    heading1 = models.CharField(max_length=100)
    heading2 = models.CharField(max_length=100)
    description = models.TextField()

    card_heading = models.CharField(max_length=150, blank=True, null=True)
    card_description = models.TextField(blank=True, null=True)
    icon = CloudinaryField('icon', blank=True, null=True)  # cloudinary icon

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.heading1} - {self.heading2}"
