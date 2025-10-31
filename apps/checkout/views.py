from rest_framework import generics, permissions
from .models import Shipping
from .serializers import ShippingSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from rest_framework import generics, permissions, status
from rest_framework.response import Response


# # create and list shipping info
# class ShippingListCreateView(generics.ListCreateAPIView):
#     serializer_class = ShippingSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = None

#     def get_queryset(self):
#         return Shipping.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         user = self.request.user
#         order = serializer.validated_data.get('order')
#         # prevent duplicate shipping for same order
#         if order and Shipping.objects.filter(user=user, order=order).exists():
#             raise ValidationError({"detail": "Shipping info for this order already exists."})
#         serializer.save(user=user)


class ShippingListCreateView(generics.ListCreateAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Return all shipping addresses for the logged-in user
        return Shipping.objects.filter(user=self.request.user).order_by('-is_default', '-id')

    def perform_create(self, serializer):
        user = self.request.user
        order = serializer.validated_data.get('order')
        is_default = serializer.validated_data.get('is_default', False)

        # Prevent duplicate shipping info for the same order
        if order and Shipping.objects.filter(user=user, order=order).exists():
            raise ValidationError({"detail": "Shipping info for this order already exists."})

        # If user wants this address as default, unset others
        if is_default:
            Shipping.objects.filter(user=user, is_default=True).update(is_default=False)
        else:
            # If user has no shipping addresses yet, set this as default automatically
            if not Shipping.objects.filter(user=user).exists():
                serializer.validated_data['is_default'] = True

        serializer.save(user=user)


# delete and update shipping info
class ShippingRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Shipping.objects.all()
        return Shipping.objects.filter(user=user)

    def get_object(self):
        try:
            return self.get_queryset().get(id=self.kwargs["id"])
        except Shipping.DoesNotExist:
            raise NotFound(detail="Shipping not found for this user or invalid ID.")

