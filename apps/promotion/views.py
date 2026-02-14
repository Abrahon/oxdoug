from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HeroPromotion
from .serializers import HeroPromotionSerializer


# List all HeroPromotions (Public or Authenticated — your choice)
class HeroPromotionListView(generics.ListAPIView):
    queryset = HeroPromotion.objects.all().order_by('-created_at')
    serializer_class = HeroPromotionSerializer
    permission_classes = [permissions.AllowAny]  # or IsAuthenticated


# Retrieve & Update single HeroPromotion
class HeroPromotionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = HeroPromotion.objects.all()
    serializer_class = HeroPromotionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
