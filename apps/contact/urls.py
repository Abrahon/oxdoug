# apps/contact/urls.py
from django.urls import path
from .views import (
    ContactMessageCreateAPIView,
    AdminContactMessageListAPIView,
    AdminReplyAPIView,
    AdminContactMessageDeleteAPIView,
)

urlpatterns = [
    # User sends a message
    path('send/message/', ContactMessageCreateAPIView.as_view(), name='contact-create'),

    # Admin lists all messages
    path('contact/admin/', AdminContactMessageListAPIView.as_view(), name='contact-admin-list'),

    # Admin replies to message
    path('contact/admin/reply/<int:id>/', AdminReplyAPIView.as_view(), name='contact-admin-reply'),

    # Admin deletes message
    path('contact/admin/<int:id>/', AdminContactMessageDeleteAPIView.as_view(), name='contact-admin-delete'),
]
