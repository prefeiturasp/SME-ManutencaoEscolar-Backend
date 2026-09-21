"""Views da API do domínio Profissional."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.viewsets import ModelViewSet

from apps.profissional.filters import ProfissionalFilter
from apps.profissional.models import Profissional
from apps.profissional.schemas import PROFISSIONAL_SCHEMA
from apps.profissional.serializers.profissional_serializers import (
    ProfissionalCriarAtualizarSerializer,
    ProfissionalSerializer,
)
from apps.profissional.services.profissional_services import (
    ProfissionalService,
)
from apps.usuarios.models import Usuario


@PROFISSIONAL_SCHEMA
class ProfissionalViewSet(ModelViewSet):
    """Disponibiliza o cadastro de profissionais."""

    queryset = Profissional.objects.prefetch_related(
        "funcoes__cargo", "funcoes__documentos"
    )
    lookup_field = "uuid"
    http_method_names = ["post", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfissionalFilter

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ProfissionalService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer apropriado para a ação atual."""
        if self.action == "create":
            return ProfissionalCriarAtualizarSerializer
        return ProfissionalSerializer

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado, quando houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria o profissional por meio da camada de serviço."""
        try:
            serializer.instance = self.service.criar(
                serializer.validated_data, self._usuario_logado()
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc
