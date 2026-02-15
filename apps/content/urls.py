from django.urls import path
from .views import WhyChooseRetrieveUpdateView, WhyChooseCreateView

urlpatterns = [
    path('why-choose/', WhyChooseRetrieveUpdateView.as_view(), name='why-choose'),  # GET & PUT/PATCH
    path('why-choose/create/', WhyChooseCreateView.as_view(), name='why-choose-create'),  # POST
]
