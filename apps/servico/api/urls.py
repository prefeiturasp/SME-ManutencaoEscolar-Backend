"""Rotas da API do domínio Serviço."""

from rest_framework.routers import DefaultRouter

from apps.servico.api.views import ServicoViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(r"servicos", ServicoViewSet)

urlpatterns = router.urls
