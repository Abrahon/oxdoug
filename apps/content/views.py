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
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Section
from .serializers import SectionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser



class WhyChooseSectionDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        return get_object_or_404(WhyChooseSection, pk=pk)

    def get(self, request, pk):
        section = self.get_object(pk)
        serializer = WhyChooseSectionSerializer(section)
        return Response(serializer.data)

    def put(self, request, pk):
        section = self.get_object(pk)
        serializer = WhyChooseSectionSerializer(section, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        section = self.get_object(pk)
        serializer = WhyChooseSectionSerializer(section, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class WhyChooseSectionListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        sections = WhyChooseSection.objects.all().order_by('-created_at')
        serializer = WhyChooseSectionSerializer(sections, many=True)
        return Response(serializer.data)

    def post(self, request):
        # ✅ Limit to 4 cards only
        if WhyChooseSection.objects.count() >= 4:
            return Response(
                {"detail": "Maximum 4 Why Choose cards are allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = WhyChooseSectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Card created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
class SectionSingletonView(generics.GenericAPIView):
    serializer_class = SectionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        #  Public GET
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        #  Admin for POST / PUT / PATCH
        return [permissions.IsAdminUser()]

    def get_object(self):
        return Section.objects.first()

    #  GET (Public)
    def get(self, request):
        section = self.get_object()
        if not section:
            return Response({"detail": "No section exists yet."}, status=404)

        serializer = self.get_serializer(section)
        return Response(serializer.data)

    #  POST (Admin only - create once)
    def post(self, request):
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

    #  PUT (Admin only - full update)
    def put(self, request):
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

    #  PATCH (Admin only - partial update)
    def patch(self, request):
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

    def get_permissions(self):
        # Public GET
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        # Admin for POST / PUT / PATCH / DELETE
        return [permissions.IsAdminUser()]

    def get_object(self):
        return ContactInfo.objects.first()

    #  Public GET
    def get(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists."}, status=404)

        serializer = self.get_serializer(contact)
        return Response(serializer.data)

    #  Admin POST (Create once)
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

    # Admin PUT (Full update)
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

    #  Admin PATCH (Partial update)
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

    #  Admin DELETE
    def delete(self, request):
        contact = self.get_object()
        if not contact:
            return Response({"detail": "No contact information exists to delete."}, status=404)

        contact.delete()

        return Response(
            {"detail": "Contact information deleted successfully."},
            status=status.HTTP_200_OK
        )
