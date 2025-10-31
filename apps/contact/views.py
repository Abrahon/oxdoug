# apps/contact/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import ContactMessage, MessageStatus
from .serializers import ContactMessageSerializer, AdminReplySerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# ---------------------------
# User send messsage
# ---------------------------
class ContactMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_create(self, serializer):
        # No need to pass user
        serializer.save()



# ---------------------------
# Admin list all messahe of user
# ---------------------------
class AdminContactMessageListAPIView(generics.ListAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]  

    def get_queryset(self):
        return ContactMessage.objects.all().order_by("-created_at")



# admin reply to user email
class AdminReplyAPIView(generics.GenericAPIView):
    serializer_class = AdminReplySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()
    lookup_field = "id"

    def post(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        instance.status = MessageStatus.REPLIED
        instance.replied_at = timezone.now()
        instance.save()

        # Send email
        subject = f"Reply to your message: {instance.subject}"
        message = f"Hi {instance.name},\n\n{instance.admin_reply}\n\nBest regards,\nAdmin Team"
        recipient = instance.email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False
        )

        return Response({
            "success": "Reply sent to user successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



# delete message
class AdminContactMessageDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"success": "Message deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to delete message: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

