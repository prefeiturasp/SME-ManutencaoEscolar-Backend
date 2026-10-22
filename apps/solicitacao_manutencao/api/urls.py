"""Rotas da API de solicitações de manutenção."""

from rest_framework.routers import DefaultRouter

from apps.solicitacao_manutencao.api.views import (
    SolicitacaoManutencaoViewSet,
)

router = DefaultRouter()
router.trailing_slash = "/?"
router.register(
    r"solicitacoes-manutencao",
    SolicitacaoManutencaoViewSet,
)

urlpatterns = router.urls
