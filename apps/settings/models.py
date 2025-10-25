from django.db import models
from django.conf import settings 

# Create your models here.
class EmailSecurity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="emailsecurity_profile")
    backup_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.email  