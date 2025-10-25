# apps/contact/models.py
from django.db import models
from django.conf import settings
from .enums import MessageStatus

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=MessageStatus.choices, default=MessageStatus.NEW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} - {self.email}"
