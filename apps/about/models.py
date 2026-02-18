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




class JoinOurJourney(models.Model):
    description = models.TextField()
    image = CloudinaryField('join_our_journey_image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Join Our Journey"

    class Meta:
        verbose_name = "Join Our Journey"
        verbose_name_plural = "Join Our Journey"
