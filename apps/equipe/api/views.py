"""Views da API do domínio Equipe."""

from collections.abc import Callable
from typing import Any, cast

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.filters import EquipeFilter
from apps.equipe.models import Equipe
from apps.equipe.schemas import EQUIPE_SCHEMA
from apps.equipe.serializers import (
    EquipeCriarEditarSerializer,
    EquipeListSerializer,
)
from apps.equipe.services import EquipeService
from apps.usuarios.models import Usuario


@EQUIPE_SCHEMA
class EquipeViewSet(
    CreateModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet
):
    """Disponibiliza o cadastro e a listagem de equipes."""

    queryset = Equipe.objects.all()
    serializer_class = EquipeCriarEditarSerializer
    http_method_names = ["post", "options", "get", "put", "patch"]
    lookup_field = "uuid"
    filter_backends = [DjangoFilterBackend]
    filterset_class = EquipeFilter

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de equipes."""
        super().__init__(**kwargs)
        self.service = EquipeService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer apropriado para a ação atual."""
        if self.action in {"create", "update", "partial_update"}:
            return EquipeCriarEditarSerializer
        return EquipeListSerializer

    def _obter_usuario(self) -> Usuario:
        """Retorna o usuário autenticado."""
        usuario = self.request.user

        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")

        return usuario

    def _executar_operacao(
        self, operacao: Callable[[], dict[str, Any]]
    ) -> dict[str, Any]:
        """Execute uma operação convertendo seus erros em erros da API."""
        try:
            return operacao()
        except (
            EquipeJaCadastradaError,
            ProfissionaisVinculadosError,
            ProfissionalVinculadoError,
        ) as exc:
            raise DRFValidationError(
                {"title": exc.title, "detail": exc.detail}
            ) from exc
        except DjangoValidationError as exc:
            detalhes = getattr(exc, "message_dict", exc.messages)
            raise DRFValidationError(detalhes) from exc

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria uma equipe pela camada de serviço.

        Args:
            serializer: Serializer validado com os dados da nova equipe.

        Raises:
            DRFValidationError: Se a equipe já estiver cadastrada, houver
                profissionais vinculados ou os dados forem inválidos.
        """
        usuario = self._obter_usuario()
        serializer.instance = self._executar_operacao(
            lambda: self.service.criar(serializer.validated_data, usuario)
        )

    def perform_update(self, serializer: BaseSerializer) -> None:
        """Atualiza uma equipe pela camada de serviço.

        Args:
            serializer: Serializer validado com os dados da equipe a ser
                atualizada.

        Raises:
            DRFValidationError: Se houver profissionais vinculados ou os
                dados forem inválidos.
        """
        usuario = self._obter_usuario()
        equipe = cast(Equipe, serializer.instance)
        serializer.instance = self._executar_operacao(
            lambda: self.service.atualizar(
                equipe, serializer.validated_data, usuario
            )
        )
