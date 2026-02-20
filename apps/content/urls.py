from django.urls import path
from .views import WhyChooseSectionListCreateAPIView, WhyChooseSectionDetailAPIView, DERListCreateView, DERRetrieveUpdateDestroyView,SectionSingletonView,ContactInfoSingletonView

urlpatterns = [

    path('why-choose/', WhyChooseSectionListCreateAPIView.as_view(), name='why-choose-list-create'),
    path('why-choose/<int:pk>/', WhyChooseSectionDetailAPIView.as_view(), name='why-choose-detail'),


    path('how-works/', DERListCreateView.as_view(), name='der-list-create'),
    path('how-works/<int:pk>/', DERRetrieveUpdateDestroyView.as_view(), name='der-detail'),
    # section

    path('section/', SectionSingletonView.as_view(), name='section-singleton'),
    # contact info
    path('contact-info/', ContactInfoSingletonView.as_view(), name='contact-info-singleton'),

]
