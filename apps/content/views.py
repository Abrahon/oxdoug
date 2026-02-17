from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import WhyChooseSection
from .serializers import WhyChooseSectionSerializer

# GET all & POST new
class WhyChooseSectionView(generics.ListCreateAPIView):
    queryset = WhyChooseSection.objects.all()
    serializer_class = WhyChooseSectionSerializer
    parser_classes = [MultiPartParser, FormParser]  # Important for file upload

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

# GET single & update
class WhyChooseSectionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = WhyChooseSection.objects.all()
    serializer_class = WhyChooseSectionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
