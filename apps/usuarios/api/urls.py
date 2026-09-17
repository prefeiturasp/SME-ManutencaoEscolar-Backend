"""Rotas da API do domínio Usuários."""

from rest_framework.routers import DefaultRouter

from apps.usuarios.api.views.cargo_eol_views import CargoEOLViewSet
from apps.usuarios.api.views.usuario_views import UsuarioViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(
    r"usuarios",
    UsuarioViewSet,
    basename="usuarios",
)
router.register(
    r"cargos-eol",
    CargoEOLViewSet,
    basename="cargos-eol",
)

urlpatterns = router.urls
