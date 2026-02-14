from django.urls import path
from .views import HeroPromotionListView, HeroPromotionRetrieveUpdateView

urlpatterns = [
    path('hero-promotions/', HeroPromotionListView.as_view(), name='hero-promotion-list'),
    path('hero-promotions/<int:pk>/', HeroPromotionRetrieveUpdateView.as_view(), name='hero-promotion-detail-update'),
]
