from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from .models import EmailSecurity
from .serializers import EmailSecuritySerializer, ChangePasswordSerializer


# ---------------------- Email Security ---------------------- #

class EmailSecurityDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = EmailSecuritySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        """
        Get or create the EmailSecurity object for the current admin user.
        """
        obj, created = EmailSecurity.objects.get_or_create(user=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        """
        Clean response wrapper with success message.
        """
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Admin email updated successfully",
                "data": response.data
            },
            status=status.HTTP_200_OK
        )




# ---------------------- Change Password ---------------------- #
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, serializer.instance)
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
