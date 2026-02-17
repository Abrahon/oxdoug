from django.urls import path
from .views import WhyChooseSectionView, WhyChooseSectionRetrieveUpdateView, DERListCreateView, DERRetrieveUpdateDestroyView,SectionSingletonView,ContactInfoSingletonView

urlpatterns = [
    path('why-choose/', WhyChooseSectionView.as_view()),
    path('why-choose/<int:pk>/', WhyChooseSectionRetrieveUpdateView.as_view()),


    path('how-works/', DERListCreateView.as_view(), name='der-list-create'),
    path('how-works/<int:pk>/', DERRetrieveUpdateDestroyView.as_view(), name='der-detail'),
    # section

    path('section/', SectionSingletonView.as_view(), name='section-singleton'),
    # contact info
    path('contact-info/', ContactInfoSingletonView.as_view(), name='contact-info-singleton'),

]
