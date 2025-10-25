# apps/contact/serializers.py
from rest_framework import serializers
from .models import ContactMessage, MessageStatus

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = ["status", "admin_reply", "replied_at", "created_at"]

class AdminReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["admin_reply"]
