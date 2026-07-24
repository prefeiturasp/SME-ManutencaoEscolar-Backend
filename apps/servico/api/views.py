"""Views DRF do domínio Serviço (finas: validam e delegam ao service)."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.serializers import BaseSerializer

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.models import Servico
from apps.servico.schemas import SERVICO_SCHEMA
from apps.servico.serializers import ServicoCriarSerializer
from apps.servico.services.servico_service import ServicoService


class ServicoInstabilidadeError(APIException):
    """Exceção lançada quando o serviço está instável."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = ServicoErrorMessages.INSTABILIDADE
    default_code = "servico_instabilidade"


@SERVICO_SCHEMA
class ServicoViewSet(viewsets.ModelViewSet):
    """CRUD + ações de Servico.

    Delegando regras de negócio ao ServicoService.
    """

    permission_classes = [AllowAny]
    queryset = Servico.objects.all()
    http_method_names = ["post", "options"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ServicoService()

    # ---- serializer por ação ----
    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "create":
            return ServicoCriarSerializer
        return ServicoCriarSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        try:
            servico = self.service.criar(serializer.validated_data)
        except ServicoJaCadastradoError as exc:
            raise DRFValidationError(
                {
                    "title": exc.title,
                    "detail": exc.detail,
                }
            ) from exc
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise DRFValidationError(exc.message_dict) from exc
            raise DRFValidationError(exc.messages) from exc
        except Exception as exc:
            raise ServicoInstabilidadeError(
                {
                    "title": "Erro",
                    "detail": ServicoErrorMessages.INSTABILIDADE,
                }
            ) from exc

        serializer.instance = servico
