from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FAQ
from .serializers import FAQSerializer
from rest_framework import generics, permissions
from .models import ShippingPolicy
from .serializers import ShippingPolicySerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ReturnPolicy
from .serializers import ReturnPolicySerializer
from .models import TermsAndConditions
from .serializers import TermsAndConditionsSerializer

from rest_framework.exceptions import ValidationError
from .models import ReturnHelp
from .serializers import ReturnHelpSerializer



class FAQListCreateAPIView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class FAQRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return Response(
            {"detail": "FAQ deleted successfully."},
            status=status.HTTP_200_OK
        )
# shipping


# Public GET, Admin create/update/delete
class ShippingPolicyListCreateView(generics.ListCreateAPIView):
    queryset = ShippingPolicy.objects.all().order_by('-created_at')
    serializer_class = ShippingPolicySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # public GET
        return [permissions.IsAdminUser()]   # admin for POST


class ShippingPolicyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShippingPolicy.objects.all()
    serializer_class = ShippingPolicySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Public GET
        return [permissions.IsAdminUser()]   # Admin-only for PUT/PATCH/DELETE

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "detail": "Shipping policy updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Shipping policy deleted successfully."},
            status=status.HTTP_200_OK
        )

# return polecy


class ReturnPolicyListCreateView(generics.ListCreateAPIView):
    queryset = ReturnPolicy.objects.all()
    serializer_class = ReturnPolicySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # public GET
        return [permissions.IsAdminUser()]  # admin for POST

class ReturnPolicyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReturnPolicy.objects.all()
    serializer_class = ReturnPolicySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # public GET
        return [permissions.IsAdminUser()]  # admin for PUT/PATCH/DELETE

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"detail": "Return policy updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Return policy deleted successfully."},
            status=status.HTTP_200_OK
        )

# terms and condition


class TermsAndConditionsListCreateView(generics.ListCreateAPIView):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class TermsAndConditionsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"detail": "Terms & Conditions updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Terms & Conditions deleted successfully."},
            status=status.HTTP_200_OK
        )

# return views


class ReturnHelpListCreateView(generics.ListCreateAPIView):
    queryset = ReturnHelp.objects.all()
    serializer_class = ReturnHelpSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Public GET
        return [permissions.IsAdminUser()]  # Admin POST

    def perform_create(self, serializer):
        if ReturnHelp.objects.exists():
            raise ValidationError(
                {"detail": "ReturnHelp instance already exists. You can update or delete it."}
            )
        serializer.save()


class ReturnHelpRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReturnHelp.objects.all()
    serializer_class = ReturnHelpSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Public GET
        return [permissions.IsAdminUser()]  # Admin PUT/PATCH/DELETE

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "ReturnHelp instance deleted successfully."})