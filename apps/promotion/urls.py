from django.urls import path
from .views import HeroPromotionSingletonView

urlpatterns = [
    path('hero-promotion/', HeroPromotionSingletonView.as_view(), name='hero-promotion'),
]
