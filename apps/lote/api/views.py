"""Views DRF do domínio de lotes."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
)
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import (
    DREJaVinculadaError,
    LoteJaCadastradoError,
)
from apps.lote.models import Lote
from apps.lote.schemas import LOTE_SCHEMA
from apps.lote.serializers import (
    LoteCriarSerializer,
    LoteSerializer,
)
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


class LoteInstabilidadeError(APIException):
    """Representa uma instabilidade durante o cadastro do lote."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = LoteErrorMessages.INSTABILIDADE
    default_code = "lote_instabilidade"


@LOTE_SCHEMA
class LoteViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Disponibiliza o cadastro de lotes."""

    http_method_names = ["post", "options"]
    queryset = Lote.objects.all()

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de lotes."""
        super().__init__(**kwargs)
        self.service = LoteService()

    def _obter_usuario(self) -> Usuario:
        """Retorna o usuário autenticado."""
        usuario = self.request.user

        if not isinstance(usuario, Usuario):
            raise NotAuthenticated(
                "Usuário não identificado."
            )

        return usuario

    def get_serializer_class(self) -> type[BaseSerializer]:
            """Retorna o serializer adequado para cada ação."""
            if self.action == "create":
                return LoteCriarSerializer

            return LoteSerializer

    def perform_create(
        self,
        serializer: BaseSerializer
    ) -> None:
        """Cria um lote delegando as regras ao lote."""

        usuario = self._obter_usuario()

        try:
            lote = self.service.criar(
                dados=serializer.validated_data,
                usuario=usuario,
            )
        except DREJaVinculadaError as exc:
            raise DRFValidationError(
                {
                    "title": exc.title,
                    "detail": exc.detail,
                }
            ) from exc
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise DRFValidationError(
                    exc.message_dict,
                ) from exc

            raise DRFValidationError(exc.messages) from exc
        except Exception as exc:
            raise LoteInstabilidadeError(
                {
                    "title": "Erro",
                "detail": LoteErrorMessages.INSTABILIDADE,
                }
            ) from exc

        serializer.instance = lote
