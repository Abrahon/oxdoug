from django.urls import path
from .views import WhyChooseSectionView, WhyChooseSectionRetrieveUpdateView

urlpatterns = [
    path('why-choose/', WhyChooseSectionView.as_view()),
    path('why-choose/<int:pk>/', WhyChooseSectionRetrieveUpdateView.as_view()),
]
