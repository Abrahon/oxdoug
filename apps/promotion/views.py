from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HeroPromotion
from .serializers import HeroPromotionSerializer


# List all HeroPromotions (Public or Authenticated — your choice)
class HeroPromotionListView(generics.ListAPIView):
    queryset = HeroPromotion.objects.all().order_by('-created_at')
    serializer_class = HeroPromotionSerializer
    permission_classes = [permissions.AllowAny]  


# # Retrieve & Update single HeroPromotion
# class HeroPromotionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
#     queryset = HeroPromotion.objects.all()
#     serializer_class = HeroPromotionSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     def get_permissions(self):
#         if self.request.method in ['PUT', 'PATCH']:
#             return [permissions.IsAdminUser()]
#         return [permissions.AllowAny()]



from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HeroPromotion
from .serializers import HeroPromotionSerializer


class HeroPromotionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = HeroPromotionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAdminUser()]  # only admin can update
        return [permissions.AllowAny()]  # everyone can GET

    def get_object(self):
        """
        Return the latest HeroPromotion instance.
        If none exists, create a new one.
        """
        instance = HeroPromotion.objects.order_by('-created_at').first()
        if not instance:
            instance = HeroPromotion.objects.create(
                title1="",
                title2="",
                description=""
            )
        return instance
