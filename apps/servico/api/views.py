"""Views DRF do domínio Serviço (finas: validam e delegam ao service)."""
from django.conf import settings
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.serializers import BaseSerializer

from apps.core.pagination import PaginacaoPadrao
from apps.servico.constants import ServicoErrorMessages
from apps.servico.exceptions import ServicoJaCadastradoError
from apps.servico.filters import ServicoFilter
from apps.servico.models import Servico
from apps.servico.schemas import SERVICO_SCHEMA
from apps.servico.serializers import ServicoAtualizarSerializer, ServicoCriarSerializer, ServicoSerializer
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
    http_method_names = ["get", "post", "patch", "options"]
    queryset = Servico.objects.all()
    lookup_field = "uuid"
    
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServicoFilter
    pagination_class = PaginacaoPadrao

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.service = ServicoService()

    # ---- serializer por ação ----
    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer adequado para cada ação."""
        if self.action == "create":
            return ServicoCriarSerializer

        if self.action in {"update", "partial_update"}:
            return ServicoAtualizarSerializer

        return ServicoSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Criando um serviço delegando as regras ao service."""
        try:
            servico = self.service.criar(serializer.validated_data,
                                         usuario_id=self.request.user.pk)
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

    def perform_update(self, serializer: BaseSerializer) -> None:
        """Atualiza um serviço delegando as regras ao service."""
        try:
            servico_atualizado = self.service.atualizar(
                servico=serializer.instance,
                dados=serializer.validated_data,
                usuario_id=self.request.user.pk,
            )
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
                    "detail": ServicoErrorMessages.ERRO_AO_ATUALIZAR,
                }
            ) from exc

        serializer.instance = servico_atualizado
