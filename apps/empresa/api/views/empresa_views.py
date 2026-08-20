"""Views DRF do domínio Empresa.

Responsáveis pela validação e delegação ao serviço.
"""

from typing import Any, cast

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import (
    BaseSerializer,
)
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.viewsets import ModelViewSet

from apps.empresa.exceptions import EmpresaCnpjDuplicadoError
from apps.empresa.filters import EmpresaFilter
from apps.empresa.models import Empresa
from apps.empresa.schemas.empresa_schemas import EMPRESA_SCHEMA
from apps.empresa.serializers.empresa_serializers import (
    EmpresaCriarAtualizarSerializer,
    EmpresaSerializer,
)
from apps.empresa.services.empresa_service import EmpresaService
from apps.usuarios.models import Usuario


@EMPRESA_SCHEMA
class EmpresaViewSet(ModelViewSet):
    """CRUD + ações de Empresa.

    Delegando regras de negócio ao EmpresaService.
    """

    queryset = Empresa.objects.all()
    lookup_field = "uuid"
    http_method_names = ["get", "post", "put", "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmpresaFilter

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = EmpresaService()

    # ---- serializer por ação ----
    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer apropriado para a ação atual."""
        if self.action in ("create", "update"):
            return EmpresaCriarAtualizarSerializer
        return EmpresaSerializer

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado da requisição, se houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Cria uma nova empresa usando o serviço.

        Args:
            serializer (BaseSerializer): Serializer contendo os dados da
                empresa.

        Raises:
            DRFValidationError: Se ocorrer algum erro de validação.
        """
        try:
            empresa = self.service.criar(
                serializer.validated_data, self._usuario_logado()
            )
        except EmpresaCnpjDuplicadoError as exc:
            raise DRFValidationError({"cnpj": str(exc)}) from exc
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = empresa

    def perform_update(self, serializer: BaseSerializer) -> None:
        """
        Atualiza uma empresa existente usando o serviço.

        Args:
            serializer (BaseSerializer): Serializer contendo os dados da
                empresa.

        Raises:
            DRFValidationError: Se ocorrer algum erro de validação.
        """
        try:
            empresa = self.service.atualizar(
                cast(Empresa, serializer.instance),
                serializer.validated_data,
                self._usuario_logado(),
            )
        except EmpresaCnpjDuplicadoError as exc:
            raise DRFValidationError({"cnpj": str(exc)}) from exc
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = empresa

    def perform_destroy(self, instance: Empresa) -> None:
        """
        Deleta uma empresa existente usando o serviço.

        Args:
            instance (Empresa): Instância da empresa a ser deletada.
        Raises:
            DRFValidationError: Se ocorrer algum erro de validação.
        """
        self.service.deletar(instance, self._usuario_logado())
