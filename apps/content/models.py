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


# how it is workes

class DER(models.Model):
    icon = CloudinaryField('icon', blank=True, null=True)  # cloudinary icon
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# section
class Section(models.Model):
    # Heading 1
    heading1 = models.CharField(max_length=255)
    description1 = models.TextField(blank=True, null=True)
    icon1 = CloudinaryField('icon1', blank=True, null=True)

    # Heading 2
    heading2 = models.CharField(max_length=255, blank=True, null=True)
    description2 = models.TextField(blank=True, null=True)
    icon2 = CloudinaryField('icon2', blank=True, null=True)

    # Heading 3
    heading3 = models.CharField(max_length=255, blank=True, null=True)
    description3 = models.TextField(blank=True, null=True)
    icon3 = CloudinaryField('icon3', blank=True, null=True)

    # Heading 4
    heading4 = models.CharField(max_length=255, blank=True, null=True)
    description4 = models.TextField(blank=True, null=True)
    icon4 = CloudinaryField('icon4', blank=True, null=True)

    # Overall image for the section
    image = CloudinaryField('image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # track updates

    def __str__(self):
        return "Section Content"

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Section"


# contact information
class ContactInfo(models.Model):
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contact Info ({self.email})"

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"