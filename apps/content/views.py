from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import WhyChooseSection
from .serializers import WhyChooseSectionSerializer
from rest_framework import generics, permissions
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import DER
from .serializers import DERSerializer

# GET all & POST new
class WhyChooseSectionView(generics.ListCreateAPIView):
    queryset = WhyChooseSection.objects.all().order_by('-created_at')
    # queryset = DER.objects.all().order_by('-created_at')
    serializer_class = WhyChooseSectionSerializer

    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  


# GET single & update
class WhyChooseSectionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = WhyChooseSection.objects.all()
    serializer_class = WhyChooseSectionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# how works

# List and Create
class DERListCreateView(generics.ListCreateAPIView):
    queryset = DER.objects.all().order_by('-created_at')
    serializer_class = DERSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  


# Retrieve, Update, Delete


class DERRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DER.objects.all()
    serializer_class = DERSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def delete(self, request, *args, **kwargs):
        # Only allow admin users to delete
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete this item."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(self.get_object())
        return Response(
            {"detail": "DER item deleted successfully."},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "detail": "DER item updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

