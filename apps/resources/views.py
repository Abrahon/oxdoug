from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FAQ
from .serializers import FAQSerializer
from rest_framework import generics, permissions
from .models import ShippingPolicy
from .serializers import ShippingPolicySerializer


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
            return [permissions.AllowAny()]  # public GET
        return [permissions.IsAdminUser()]   # admin for PUT/PATCH/DELETE