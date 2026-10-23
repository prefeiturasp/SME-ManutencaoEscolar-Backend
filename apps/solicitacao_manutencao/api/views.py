"""Views da API de solicitações de manutenção."""

from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from apps.solicitacao_manutencao.constants import (
    FaseSolicitacao,
    SituacaoSolicitacao,
    TipoAtendimento,
)
from apps.solicitacao_manutencao.filters import SolicitacaoManutencaoFilter
from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.repository import (
    SolicitacaoManutencaoRepository,
)
from apps.solicitacao_manutencao.schemas import SOLICITACAO_MANUTENCAO_SCHEMA
from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
    SolicitacaoManutencaoListSerializer,
)
from apps.solicitacao_manutencao.services.ue_services import (
    SolicitacaoManutencaoUeService,
)
from apps.usuarios.models import Usuario


@SOLICITACAO_MANUTENCAO_SCHEMA
class SolicitacaoManutencaoViewSet(ListModelMixin, GenericViewSet):
    """Disponibiliza a criação e listagem de solicitações."""

    queryset = SolicitacaoManutencao.objects.all()
    http_method_names = ["get", "post", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SolicitacaoManutencaoFilter

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer apropriado para a ação atual."""
        if self.action == "list":
            return SolicitacaoManutencaoListSerializer
        return SolicitacaoManutencaoCriarSerializer

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado, quando houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def get_queryset(
        self,
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Retorna as solicitações visíveis para o usuário autenticado."""
        return SolicitacaoManutencaoRepository().listar_por_usuario(
            self._usuario_logado()
        )

    @action(detail=False, methods=["get"], url_path="situacoes")
    def situacoes(self, request: Request) -> Response:
        """Retorna as situações disponíveis para uma solicitação.

        Args:
            request: Requisição para consulta das situações.

        Returns:
            Resposta com os valores e rótulos das situações.
        """
        return Response(
            [
                {"value": choice.value, "label": choice.label}
                for choice in SituacaoSolicitacao
            ],
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="fases")
    def fases(self, request: Request) -> Response:
        """Retorna as fases disponíveis para uma solicitação.

        Args:
            request: Requisição para consulta das fases.

        Returns:
            Resposta com os valores e rótulos das fases.
        """
        return Response(
            [
                {"value": choice.value, "label": choice.label}
                for choice in FaseSolicitacao
            ],
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="tipos-atendimento")
    def tipos_atendimento(self, request: Request) -> Response:
        """Retorna os tipos de atendimento disponíveis.

        Args:
            request: Requisição para consulta dos tipos de atendimento.

        Returns:
            Resposta com os valores e rótulos dos tipos de atendimento.
        """
        return Response(
            [
                {"value": choice.value, "label": choice.label}
                for choice in TipoAtendimento
            ],
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="solicitacao-ue")
    def solicitacao_ue(self, request: Request) -> Response:
        """Cria uma solicitação de manutenção para uma UE.

        Args:
            request: Requisição com os dados da solicitação.

        Returns:
            Resposta com os dados da solicitação criada.

        Raises:
            NotAuthenticated: Se o usuário autenticado não for identificado.
        """
        usuario = request.user
        socitacao_service = SolicitacaoManutencaoUeService()
        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enviar = request.query_params.get("enviar") == "true"
        serializer.instance = socitacao_service.criar(
            serializer.validated_data,
            usuario,
            enviar=enviar,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
