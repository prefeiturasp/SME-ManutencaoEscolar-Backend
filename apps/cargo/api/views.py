"""Views DRF do domínio de cargos."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import BaseSerializer

from apps.cargo.constants import CargoErrorMessages
from apps.cargo.models import Cargo
from apps.cargo.schemas import CARGO_SCHEMA
from apps.cargo.serializers import CargoCriarSerializer
from apps.cargo.services.cargo_service import CargoService
from apps.usuarios.models.usuario import Usuario


class CargoInstabilidadeError(APIException):
    """Representa uma instabilidade durante o cadastro do cargo."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Não foi possível cadastrar o cargo."
    default_code = "cargo_instabilidade"


@CARGO_SCHEMA
class CargoViewSet(viewsets.ModelViewSet):
    """CRUD + ações de Cargos.

    Delegando regras de negócio ao CargosService.
    """

    http_method_names = ["post", "options"]
    queryset = Cargo.objects.all()
    serializer_class = CargoCriarSerializer

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de cargos.

        Args:
            **kwargs: Argumentos adicionais utilizados na inicialização
                da view.
        """
        super().__init__(**kwargs)
        self.service = CargoService()

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
