from django.urls import path
from .views import FAQListCreateAPIView, FAQRetrieveUpdateDestroyAPIView,ShippingPolicyListCreateView, ShippingPolicyRetrieveUpdateDestroyView

urlpatterns = [
    path("faqs/", FAQListCreateAPIView.as_view(), name="faq-list-create"),
    path("faqs/<int:pk>/", FAQRetrieveUpdateDestroyAPIView.as_view(), name="faq-detail"),
    path('shipping-policy/', ShippingPolicyListCreateView.as_view(), name='shipping-policy-list-create'),
    path('shipping-policy/<int:pk>/', ShippingPolicyRetrieveUpdateDestroyView.as_view(), name='shipping-policy-detail'),
]