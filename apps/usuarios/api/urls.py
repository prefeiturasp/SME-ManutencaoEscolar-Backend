"""Rotas da API do domínio Usuários."""

from rest_framework.routers import DefaultRouter

from apps.usuarios.api.views import UsuarioViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(
    r"usuarios",
    UsuarioViewSet,
    basename="usuarios",
)

urlpatterns = router.urls
