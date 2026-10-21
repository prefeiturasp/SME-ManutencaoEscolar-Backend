"""Views da API de solicitações de manutenção."""

from typing import Any

from rest_framework.exceptions import NotAuthenticated
from rest_framework.mixins import CreateModelMixin
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.schemas import SOLICITACAO_MANUTENCAO_SCHEMA
from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
)
from apps.solicitacao_manutencao.services import SolicitacaoManutencaoService
from apps.usuarios.models import Usuario


@SOLICITACAO_MANUTENCAO_SCHEMA
class SolicitacaoManutencaoViewSet(CreateModelMixin, GenericViewSet):
    """Disponibiliza a criação de solicitações de manutenção."""

    queryset = SolicitacaoManutencao.objects.all()
    serializer_class = SolicitacaoManutencaoCriarSerializer
    http_method_names = ["post", "options"]

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de solicitações."""
        super().__init__(**kwargs)
        self.service = SolicitacaoManutencaoService()

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria a solicitação por meio da camada de serviço."""
        usuario = self.request.user
        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")
        enviar = self.request.query_params.get("enviar") == "true"
        serializer.instance = self.service.criar(
            serializer.validated_data,
            usuario,
            enviar=enviar,
        )
