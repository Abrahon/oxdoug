from django.urls import path
from .views import WhyChooseSectionView, WhyChooseSectionRetrieveUpdateView, DERListCreateView, DERRetrieveUpdateDestroyView,SectionRetrieveUpdateView

urlpatterns = [
    path('why-choose/', WhyChooseSectionView.as_view()),
    path('why-choose/<int:pk>/', WhyChooseSectionRetrieveUpdateView.as_view()),


    path('how-works/', DERListCreateView.as_view(), name='der-list-create'),
    path('how-works/<int:pk>/', DERRetrieveUpdateDestroyView.as_view(), name='der-detail'),
    # section
     path('section/<int:pk>/', SectionRetrieveUpdateView.as_view(), name='section-detail-update'),



]
