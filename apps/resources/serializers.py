from rest_framework import serializers
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_question(self, value):
        if FAQ.objects.filter(question__iexact=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("This question already exists.")
        return value