"""Views DRF do domínio Empresa.

Responsáveis pela validação e delegação ao serviço.
"""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from apps.empresa.exceptions import EmpresaCnpjDuplicadoError
from apps.empresa.filters import EmpresaFilter
from apps.empresa.models import Empresa
from apps.empresa.schemas import EMPRESA_SCHEMA
from apps.empresa.serializers import (
    EmpresaCriarSerializer,
    EmpresaSerializer,
)
from apps.empresa.services.empresa_service import EmpresaService


@EMPRESA_SCHEMA
class EmpresaViewSet(ModelViewSet):
    """CRUD + ações de Empresa.

    Delegando regras de negócio ao EmpresaService.
    """

    permission_classes = [AllowAny]
    queryset = Empresa.objects.all()
    http_method_names = ["post", "get"]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmpresaFilter

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = EmpresaService()

    # ---- serializer por ação ----
    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "create":
            return EmpresaCriarSerializer
        return EmpresaSerializer  # pragma: no cover

    def perform_create(self, serializer: BaseSerializer) -> None:
        try:
            empresa = self.service.criar(serializer.validated_data)
        except EmpresaCnpjDuplicadoError as exc:
            raise DRFValidationError({"cnpj": str(exc)}) from exc
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = empresa
