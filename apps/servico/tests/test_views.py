"""Views DRF do domínio Serviço."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny

from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.models import Servico
from apps.servico.schemas import SERVICO_SCHEMA
from apps.servico.serializers import ServicoCriarSerializer
from apps.servico.services.servico_service import ServicoService


class ServicoInstabilidadeError(APIException):
    """Erro de instabilidade durante o cadastro do serviço."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = {
        "title": "Erro",
        "detail": ServicoErrorMessages.INSTABILIDADE,
    }
    default_code = "servico_instabilidade"


@SERVICO_SCHEMA
class ServicoViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """View responsável pelo cadastro de serviços."""

    permission_classes = [AllowAny]
    queryset = Servico.objects.all()
    serializer_class = ServicoCriarSerializer

    def __init__(self, **kwargs):
        """Inicializa a view com o serviço de domínio."""
        super().__init__(**kwargs)
        self.service = ServicoService()

    def perform_create(self, serializer):
        """Delega a criação ao serviço de domínio."""
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
            raise DRFValidationError(exc.message_dict) from exc
        except Exception as exc:
            raise ServicoInstabilidadeError() from exc

        serializer.instance = servico
