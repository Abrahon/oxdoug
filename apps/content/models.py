from django.db import models

# Create your models here.
from django.db import models


class WhyChooseSection(models.Model):
    heading1 = models.CharField(max_length=255)
    heading2 = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.heading1} {self.heading2}"


class WhyChooseCard(models.Model):
    section = models.ForeignKey(
        WhyChooseSection,
        related_name="cards",
        on_delete=models.CASCADE
    )
    card_heading = models.CharField(max_length=255)
    card_description = models.TextField()

    # Store icon name (example: FaBolt, MdBatteryChargingFull)
    icon = models.CharField(max_length=100)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.card_heading
