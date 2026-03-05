from django.urls import path
from .views import WhyChooseSectionListCreateAPIView, WhyChooseSectionDetailAPIView, DERListView, DERRetrieveUpdateDestroyView,SectionSingletonView,ContactInfoSingletonView,HeadingSectionListCreateView,HeadingSectionRetrieveUpdateDestroyView,IconSectionListCreateView,IconSectionRetrieveUpdateDeleteView


urlpatterns = [

    path('why-choose/', WhyChooseSectionListCreateAPIView.as_view(), name='why-choose-list-create'),
    path('why-choose/<int:pk>/', WhyChooseSectionDetailAPIView.as_view(), name='why-choose-detail'),


    path('how-works/', DERListView.as_view(), name='der-list'),
    path('how-works/<int:pk>/', DERRetrieveUpdateDestroyView.as_view(), name='der-detail'),
    # section

    path('section/', SectionSingletonView.as_view(), name='section-singleton'),
    # contact info
    path('contact-info/', ContactInfoSingletonView.as_view(), name='contact-info-singleton'),
    # title
    path('heading-section/', HeadingSectionListCreateView.as_view(), name='heading-section-list-create'),
    path('heading-section/<int:pk>/', HeadingSectionRetrieveUpdateDestroyView.as_view(), name='heading-section-detail'),
    path('values-section/', IconSectionListCreateView.as_view(), name='icon-section-list-create'),
    path('values-section/<int:pk>/', IconSectionRetrieveUpdateDeleteView.as_view(), name='icon-section-rud'),


]
