from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import WhyChooseSection
from .serializers import WhyChooseSectionSerializer

# Create new WhyChoose section (Admin only)
class WhyChooseCreateView(generics.CreateAPIView):
    serializer_class = WhyChooseSectionSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


# Retrieve & Update (GET anyone, PUT/PATCH admin)
class WhyChooseRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = WhyChooseSectionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_object(self):
        """
        Always return the first section.
        Auto-create if none exists.
        """
        section, created = WhyChooseSection.objects.get_or_create(
            defaults={
                "heading1": "",
                "heading2": "",
                "description": ""
            }
        )
        return section
