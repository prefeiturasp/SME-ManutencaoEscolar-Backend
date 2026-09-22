"""Views DRF do domínio de cargos."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import BaseSerializer

from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import (
    CargoInstabilidadeError,
    CargoOuDocumentoJaVinculadaError,
)
from apps.cargo.filters import CargoFilter
from apps.cargo.models import Cargo
from apps.cargo.schemas import CARGO_SCHEMA
from apps.cargo.serializers import (
    CargoCriarSerializer,
    CargoListagemSerializer,
    CargoSerializer,
)
from apps.cargo.services.cargo_service import CargoService
from apps.core.pagination import PaginacaoPadrao
from apps.usuarios.models.usuario import Usuario


@CARGO_SCHEMA
class CargoViewSet(viewsets.ModelViewSet):
    """CRUD + ações de Cargos.

    Delegando regras de negócio ao CargosService.
    """

    http_method_names = ["get", "post", "patch", "options"]
    queryset = Cargo.objects.all()
    lookup_field = "uuid"

    serializer_class = CargoCriarSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = CargoFilter
    pagination_class = PaginacaoPadrao

    @staticmethod
    def _obter_cargo(serializer: BaseSerializer) -> Cargo:
        """Retorna a instância de cargo do serializer."""
        cargo = serializer.instance

        if not isinstance(cargo, Cargo):
            raise DRFValidationError(
                {
                    "title": "Erro",
                    "detail": "Cargo inválido ou não encontrado.",
                }
            )

        return cargo

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de cargos.

        Args:
            **kwargs: Argumentos adicionais utilizados na inicialização
                da view.
        """
        super().__init__(**kwargs)
        self.service = CargoService()

    def get_serializer_class(self) -> type[BaseSerializer]:
        """Retorna o serializer adequado para cada ação."""
        if self.action in ("create", "partial_update"):
            return CargoCriarSerializer

        if self.action == "list":
            return CargoListagemSerializer

        return CargoSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria um cargo delegando as regras ao service.

        Args:
            serializer: Serializer contendo os dados validados do cargo.

        Raises:
            DRFValidationError: Quando os dados não passam pelas validações.
            CargoInstabilidadeError: Quando ocorre um erro inesperado durante
                o cadastro.
        """
        usuario = self._obter_usuario()

        try:
            cargo = self.service.criar(
                dados=serializer.validated_data,
                usuario=usuario,
            )
        except CargoOuDocumentoJaVinculadaError as exc:
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
            raise CargoInstabilidadeError(
                {
                    "title": "Erro",
                    "detail": CargoErrorMessages.INSTABILIDADE,
                }
            ) from exc

        serializer.instance = cargo

    def perform_update(self, serializer: BaseSerializer) -> None:
        """
        Atualiza um cargo existente usando o serviço.

        Args:
            serializer (BaseSerializer): Serializer contendo os dados do
                cargo.

        Raises:
            DRFValidationError: Se ocorrer algum erro de validação.
        """
        usuario = self._obter_usuario()
        cargo = self._obter_cargo(serializer)

        try:
            self.service.atualizar(
                cargo=cargo,
                dados=serializer.validated_data,
                usuario=usuario,
            )
        except CargoOuDocumentoJaVinculadaError as exc:
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
            raise CargoInstabilidadeError(
                {
                    "title": "Erro",
                    "detail": CargoErrorMessages.INSTABILIDADE,
                }
            ) from exc

        serializer.instance = cargo

    def _obter_usuario(self) -> Usuario:
        """Retorna o usuário autenticado.

        Returns:
            Usuário autenticado responsável pelo cadastro.

        Raises:
            NotAuthenticated: Quando o usuário não foi identificado.
        """
        usuario = self.request.user

        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")

        return usuario
