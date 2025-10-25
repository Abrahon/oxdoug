# apps/contact/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import ContactMessage, MessageStatus
from .serializers import ContactMessageSerializer, AdminReplySerializer

# ---------------------------
# User views
# ---------------------------

class ContactMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

# ---------------------------
# Admin views
# ---------------------------

class AdminContactMessageListAPIView(generics.ListAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return ContactMessage.objects.all().order_by("-created_at")

class AdminReplyAPIView(generics.UpdateAPIView):
    serializer_class = AdminReplySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update status and replied_at
        instance.status = MessageStatus .REPLIED
        instance.replied_at = timezone.now()
        instance.save()

        # Send email to user
        subject = f"Reply to your message: {instance.subject}"
        message = instance.admin_reply
        recipient = instance.email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])

        return Response({
            "success": "Reply sent to user successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AdminContactMessageDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()
    lookup_field = "id"
