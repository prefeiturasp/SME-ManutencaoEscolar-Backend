"""URL configuration for core API."""

from django.urls import path

from apps.core.api.views import (
    AlterarSenhaView,
    AnexoView,
    AtualizarTokenView,
    HealthCheckView,
    LoginView,
    LogoutView,
    RedefinirSenhaView,
)

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh-token/", AtualizarTokenView.as_view(), name="refresh-token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "redefinir-senha/",
        RedefinirSenhaView.as_view(),
        name="redefinir-senha",
    ),
    path(
        "alterar-senha/",
        AlterarSenhaView.as_view(),
        name="alterar-senha",
    ),
    path(
        "upload/",
        AnexoView.as_view(),
        name="upload",
    ),
]
