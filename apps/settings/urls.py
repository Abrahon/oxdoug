from django.urls import path
from . import views

urlpatterns = [
    path("email-security/",views. EmailSecurityDetailUpdateView.as_view(), name="email-preferences"),
    path("change-password/",views. ChangePasswordView.as_view(), name="change-password"),
]
