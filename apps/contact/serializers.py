# apps/contact/serializers.py
from rest_framework import serializers
from .models import ContactMessage, MessageStatus

from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']  # name & email are writable



class AdminReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["admin_reply"]
