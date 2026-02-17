from django.db import models

from cloudinary.models import CloudinaryField

class OurStory(models.Model):
    story_description = models.TextField()
    mission_description = models.TextField()
    vision_description = models.TextField()

    image = CloudinaryField('our_story_image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Our Story Section"
