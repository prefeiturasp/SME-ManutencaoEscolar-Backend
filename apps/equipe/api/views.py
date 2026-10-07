"""Views da API do domínio Equipe."""

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from apps.equipe.exceptions import (
    EquipeJaCadastradaError,
    ProfissionaisVinculadosError,
    ProfissionalVinculadoError,
)
from apps.equipe.models import Equipe
from apps.equipe.serializers import EquipeCriarSerializer
from apps.equipe.services import EquipeService
from apps.usuarios.models import Usuario


class EquipeViewSet(CreateModelMixin, GenericViewSet):
    """Disponibiliza exclusivamente o cadastro de equipes."""

    queryset = Equipe.objects.all()
    serializer_class = EquipeCriarSerializer
    http_method_names = ["post", "options"]

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa a view com o serviço de equipes."""
        super().__init__(**kwargs)
        self.service = EquipeService()

    def _obter_usuario(self) -> Usuario:
        """Retorna o usuário autenticado."""
        usuario = self.request.user

        if not isinstance(usuario, Usuario):
            raise NotAuthenticated("Usuário não identificado.")

        return usuario

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Cria uma equipe pela camada de serviço."""
        usuario = self._obter_usuario()
        try:
            serializer.instance = self.service.criar(
                serializer.validated_data, usuario
            )
        except EquipeJaCadastradaError as exc:
            raise DRFValidationError(
                {"title": exc.title, "detail": exc.detail}
            ) from exc
        except ProfissionaisVinculadosError as exc:
            raise DRFValidationError(
                {"title": exc.title, "detail": exc.detail}
            ) from exc
        except ProfissionalVinculadoError as exc:
            raise DRFValidationError(
                {"title": exc.title, "detail": exc.detail}
            ) from exc
        except DjangoValidationError as exc:
            detalhes = getattr(exc, "message_dict", exc.messages)
            raise DRFValidationError(detalhes) from exc
