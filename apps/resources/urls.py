from django.urls import path
from .views import (
     FAQListCreateAPIView,
     FAQRetrieveUpdateDestroyAPIView,
     ShippingPolicyListCreateView,
     ShippingPolicyRetrieveUpdateDestroyView,
     ReturnPolicyListCreateView,
     ReturnPolicyRetrieveUpdateDestroyView,
     TermsAndConditionsListCreateView,
     TermsAndConditionsRetrieveUpdateDestroyView,
     ReturnHelpListCreateView,
     ReturnHelpRetrieveUpdateDestroyView,
     InfoSectionListCreateView,
     InfoSectionRetrieveUpdateDestroyView
     
)

urlpatterns = [
    path("faqs/", FAQListCreateAPIView.as_view(), name="faq-list-create"),
    path("faqs/<int:pk>/", FAQRetrieveUpdateDestroyAPIView.as_view(), name="faq-detail"),
    path('shipping-policy/', ShippingPolicyListCreateView.as_view(), name='shipping-policy-list-create'),
    path('shipping-policy/<int:pk>/', ShippingPolicyRetrieveUpdateDestroyView.as_view(), name='shipping-policy-detail'),
    path('return-policy/', ReturnPolicyListCreateView.as_view(), name='return-policy-list-create'),
    path('return-policy/<int:pk>/', ReturnPolicyRetrieveUpdateDestroyView.as_view(), name='return-policy-detail'),
    path('terms-and-conditions/', TermsAndConditionsListCreateView.as_view(), name='terms-list-create'),
    path('terms-and-conditions/<int:pk>/', TermsAndConditionsRetrieveUpdateDestroyView.as_view(), name='terms-detail'),
    path('return-help/', ReturnHelpListCreateView.as_view(), name='return-help-list-create'),
    path('return-help/<int:pk>/', ReturnHelpRetrieveUpdateDestroyView.as_view(), name='return-help-detail'),
    # footer 
    path('footer-section/', InfoSectionListCreateView.as_view(), name='info-section-list-create'),
    path('footer-section/<int:pk>/', InfoSectionRetrieveUpdateDestroyView.as_view(), name='info-section-detail'),
]