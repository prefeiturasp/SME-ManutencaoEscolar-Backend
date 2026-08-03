"""URL configuration for core API."""

from django.urls import path

from apps.core.api.views import (
    AtualizarTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh-token/", AtualizarTokenView.as_view(), name="refresh-token"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
