from django.urls import path
from .views import OurStoryView

urlpatterns = [
    path('our-story/', OurStoryView.as_view(), name='our-story'),
]
