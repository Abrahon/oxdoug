from django.db import models

# Create your models here.
from django.db import models
from cloudinary.models import CloudinaryField

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question



class ShippingPolicy(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # track updates

    def __str__(self):
        return self.heading

# return polecy

class ReturnPolicy(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.heading


# terms and condition
class TermsAndConditions(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.heading


# return help 
class ReturnHelp(models.Model):
    title = models.CharField(max_length=255, default="Need Help with a Return?")

    # Customer Service block
    heading1 = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    hours = models.CharField(max_length=100, blank=True, null=True)

    # Return Address block
    heading2 = models.CharField(max_length=255, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city_state_zip = models.CharField(max_length=255, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Return Help"
        verbose_name_plural = "Return Help"

    def __str__(self):
        return self.title


class FooterSection(models.Model):
    title = models.CharField(max_length=255)
    image = CloudinaryField('image') 
    content = models.TextField()

    def __str__(self):
        return self.title


# social accounts

class SocialLinks(models.Model):
    facebook = models.URLField(max_length=255, blank=True, null=True)
    instagram = models.URLField(max_length=255, blank=True, null=True)
    x = models.URLField(max_length=255, blank=True, null=True)  # X is the new Twitter
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Social Links"
    
    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"