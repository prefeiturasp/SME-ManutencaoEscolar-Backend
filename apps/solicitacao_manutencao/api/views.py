"""Views da API de solicitações de manutenção."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.mixins import ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.viewsets import GenericViewSet

from apps.core.exceptions import AnexoArquivoError
from apps.solicitacao_manutencao.constants import (
    FaseExecucao,
    FaseSolicitacao,
    FaseVistoria,
    SituacaoSolicitacao,
    TipoAtendimento,
)
from apps.solicitacao_manutencao.filters import SolicitacaoManutencaoFilter
from apps.solicitacao_manutencao.schemas import SOLICITACAO_MANUTENCAO_SCHEMA
from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarEditarSerializer,
    SolicitacaoManutencaoDetalheSerializer,
    SolicitacaoManutencaoListSerializer,
)
from apps.solicitacao_manutencao.services.solicitacao_service import (
    SolicitacaoManutencaoService,
)
from apps.solicitacao_manutencao.services.ue_services import (
    SolicitacaoManutencaoUeService,
)
from apps.usuarios.models import Usuario
from apps.usuarios.permissions import PermissaoSolicitacoes


@SOLICITACAO_MANUTENCAO_SCHEMA
class SolicitacaoManutencaoViewSet(ListModelMixin, GenericViewSet):
    """Disponibiliza a criação, edição e consulta de solicitações."""

    permission_classes = [PermissaoSolicitacoes]

    http_method_names = ["get", "post", "put", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SolicitacaoManutencaoFilter
    lookup_field = "uuid"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = SolicitacaoManutencaoService()
        self.solicitacao_service = SolicitacaoManutencaoUeService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer apropriado para a ação atual."""
        if self.action == "list":
            return SolicitacaoManutencaoListSerializer
        if self.action == "retrieve":
            return SolicitacaoManutencaoDetalheSerializer
        return SolicitacaoManutencaoCriarEditarSerializer

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado, quando houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def get_queryset(
        self,
    ) -> Any:
        """Retorna o queryset das solicitações visíveis ao usuário.

        Returns:
            Queryset de solicitações visíveis para o usuário autenticado.
        """
        return self.service.listar_por_usuario(self._usuario_logado())

    def retrieve(self, request: Request, uuid: str) -> Response:
        """Retorna os detalhes de uma solicitação visível pelo UUID.

        Args:
            request: Requisição de consulta.
            uuid: UUID da solicitação.

        Returns:
            Resposta com os dados detalhados da solicitação.

        Raises:
            Http404: Se a solicitação não existir ou não estiver visível.
        """
        solicitacao = self.service.get_detalhes_solicitacao(
            self._usuario_logado(), uuid
        )
        if solicitacao is None:
            raise Http404("Solicitação não encontrada.")
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="situacoes")
    def situacoes(self, request: Request) -> Response:
        """Retorna as situações disponíveis para uma solicitação.

        Args:
            request: Requisição para consulta das situações.

        Returns:
            Resposta com os valores e rótulos das situações.
        """
        return Response(
            {
                choice.value: [
                    {"value": sub_choice.value, "label": sub_choice.label}
                    for sub_choice in enum_choices
                ]
                for choice, enum_choices in (
                    (FaseSolicitacao.SOLICITACAO, SituacaoSolicitacao),
                    (FaseSolicitacao.VISTORIA, FaseVistoria),
                    (FaseSolicitacao.EXECUCAO, FaseExecucao),
                )
            },
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
        usuario = self._usuario_logado()
        if usuario is None:
            raise NotAuthenticated("Usuário não identificado.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enviar = request.query_params.get("enviar") == "true"
        serializer.instance = self.solicitacao_service.criar(
            serializer.validated_data,
            usuario,
            enviar=enviar,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["put"],
        url_path=r"editar-solicitacao-ue/(?P<uuid>[^/.]+)",
    )
    def editar_solicitacao_ue(self, request: Request, uuid: str) -> Response:
        """Atualiza uma solicitação de manutenção de uma UE.

        Args:
            request: Requisição com os dados atualizados.
            uuid: UUID da solicitação a atualizar.

        Returns:
            Resposta com os dados atualizados da solicitação.

        Raises:
            NotAuthenticated: Se o usuário autenticado não for identificado.
        """
        try:
            usuario = self._usuario_logado()
            if usuario is None:
                raise NotAuthenticated("Usuário não identificado.")
            solicitacao = self.service.get_detalhes_solicitacao(usuario, uuid)
            if solicitacao is None:
                raise Http404("Solicitação não encontrada.")
            serializer = self.get_serializer(solicitacao, data=request.data)
            serializer.is_valid(raise_exception=True)
            enviar = request.query_params.get("enviar") == "true"
            serializer.instance = self.solicitacao_service.atualizar(
                solicitacao,
                serializer.validated_data,
                usuario,
                enviar=enviar,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AnexoArquivoError as exc:
            raise DRFValidationError(
                {"title": exc.title, "detail": exc.detail}
            ) from exc
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc
