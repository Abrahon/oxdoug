

from django.urls import path
from .views import UserProfileView, AdminUserProfileListView,UpdatePasswordView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('admin/profiles/', AdminUserProfileListView.as_view(), name='admin-user-profiles'),
    path("update-password/", UpdatePasswordView.as_view(), name="update-password"),
]


