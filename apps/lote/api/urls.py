"""Rotas da API do domínio Lote."""

from rest_framework.routers import DefaultRouter

from apps.lote.api.views import LoteViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"lotes", LoteViewSet)

urlpatterns = router.urls
