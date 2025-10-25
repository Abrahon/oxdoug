# apps/contact/enums.py

from django.db import models

class MessageStatus(models.TextChoices):
    NEW = "NEW", "New"
    READ = "READ", "Read"
    REPLIED = "REPLIED", "Replied"
