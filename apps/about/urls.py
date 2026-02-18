from django.urls import path
from .views import OurStoryView,JoinOurJourneyView

urlpatterns = [
    path('our-story/', OurStoryView.as_view(), name='our-story'),
    path('join-our-journey/', JoinOurJourneyView.as_view(), name='join-our-journey'),

]
