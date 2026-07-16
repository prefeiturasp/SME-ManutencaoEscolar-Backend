"""URL configuration for core API."""

from django.urls import path

from apps.core.api.views import HealthCheckView, LoginView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("login/", LoginView.as_view(), name="login"),
]
