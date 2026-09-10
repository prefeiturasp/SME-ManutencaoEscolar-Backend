"""Rotas da API do domínio Lote."""

from rest_framework.routers import DefaultRouter

from apps.cargo.api.views import CargoViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"cargos", CargoViewSet)

urlpatterns = router.urls
