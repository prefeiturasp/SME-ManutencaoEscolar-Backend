"""Views DRF do domínio Responsável Técnico.

Responsáveis pela validação e delegação ao serviço.
"""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import (
    BaseSerializer,
)
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.viewsets import ModelViewSet

from apps.empresa.models import ResponsavelTecnico
from apps.empresa.schemas.responsavel_schemas import RESPONSAVEL_SCHEMA
from apps.empresa.serializers.responsavel_serializers import (
    ResponsavelTecnicoSerializer,
)
from apps.empresa.services.responsavel_service import ResponsavelTecnicoService
from apps.usuarios.models import Usuario


@RESPONSAVEL_SCHEMA
class ResponsavelTecnicoViewSet(ModelViewSet):
    """CRUD + ações de Responsável Técnico.

    Delegando regras de negócio ao EmpresaService.
    """

    queryset = ResponsavelTecnico.objects.all()
    serializer_class = ResponsavelTecnicoSerializer
    lookup_field = "uuid"
    http_method_names = ["post"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ResponsavelTecnicoService()

    def _usuario_logado(self) -> Usuario | None:
        """Retorna o usuário autenticado da requisição, se houver."""
        usuario = self.request.user
        return usuario if usuario.is_authenticated else None

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria um novo responsável técnico usando o serviço."""
        try:
            responsavel = self.service.criar(
                serializer.validated_data, self._usuario_logado()
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict) from exc

        serializer.instance = responsavel
