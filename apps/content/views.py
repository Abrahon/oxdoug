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
from .serializers import SectionSerializer
from .models import Section
from .models import ContactInfo
from .serializers import ContactInfoSerializer

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

# section



from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Section
from .serializers import SectionSerializer

class SectionSingletonView(generics.GenericAPIView):
    serializer_class = SectionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAdminUser]  # Only admin can create/update

    def get_object(self):
        """Return the single Section object, or None"""
        return Section.objects.first()

    def get(self, request):
        section = self.get_object()
        if not section:
            return Response({"detail": "No section exists yet."}, status=404)
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    def post(self, request):
        """Create the Section only if it does not exist yet"""
        if Section.objects.exists():
            return Response(
                {"detail": "Section already exists. Use PUT/PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Section created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def put(self, request):
        """Full update"""
        section = self.get_object()
        if not section:
            return Response({"detail": "No section exists to update."}, status=404)
        serializer = self.get_serializer(section, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Section updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        """Partial update"""
        section = self.get_object()
        if not section:
            return Response({"detail": "No section exists to update."}, status=404)
        serializer = self.get_serializer(section, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Section updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

# contact info views


class ContactInfoSingletonView(generics.GenericAPIView):
    serializer_class = ContactInfoSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return ContactInfo.objects.first()

    def get(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists."}, status=404)
        serializer = self.get_serializer(contact)
        return Response(serializer.data)

    def post(self, request):
        if ContactInfo.objects.exists():
            return Response(
                {"detail": "Contact information already exists. Use PUT/PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Contact information created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def put(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists to update."}, status=404)
        serializer = self.get_serializer(contact, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Contact information updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists to update."}, status=404)
        serializer = self.get_serializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Contact information updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists to delete."}, status=404)
        contact.delete()
        return Response({"detail": "Contact information deleted successfully."}, status=status.HTTP_200_OK)
