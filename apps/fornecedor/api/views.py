"""Views DRF do domínio Fornecedor (finas: validam e delegam ao service)."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from apps.fornecedor.models import Fornecedor
from apps.fornecedor.schemas import FORNECEDOR_SCHEMA
from apps.fornecedor.serializers import (
    FornecedorCreateSerializer,
    FornecedorSerializer,
)
from apps.fornecedor.services.fornecedor_service import (
    FornecedorCnpjDuplicadoError,
    FornecedorService,
)


@FORNECEDOR_SCHEMA
class FornecedorViewSet(ModelViewSet):
    """CRUD + ações de Fornecedor.

    Delegando regras de negócio ao FornecedorService.
    """

    permission_classes = [AllowAny]
    queryset = Fornecedor.objects.all()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = FornecedorService()

    # ---- serializer por ação ----
    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "create":
            return FornecedorCreateSerializer
        return FornecedorSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        try:
            fornecedor = self.service.criar(serializer.validated_data)
        except FornecedorCnpjDuplicadoError as exc:
            raise DRFValidationError({"cnpj": str(exc)}) from exc
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = fornecedor
