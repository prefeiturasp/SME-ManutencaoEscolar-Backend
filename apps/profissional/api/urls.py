"""Rotas da API do domínio Profissional."""

from rest_framework.routers import DefaultRouter

from apps.profissional.api.views import ProfissionalViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"profissionais", ProfissionalViewSet)

urlpatterns = router.urls
