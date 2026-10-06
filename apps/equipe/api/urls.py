"""Rotas da API do domínio Equipe."""

from rest_framework.routers import DefaultRouter

from apps.equipe.api.views import EquipeViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"equipes", EquipeViewSet)

urlpatterns = router.urls
