"""Views da API da aplicação Usuarios."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.usuarios.schemas import ME
from apps.usuarios.serializers.usuario_serializer import (
    UsuarioResponseSerializer,
)
from apps.usuarios.services.usuario_service import UsuarioService


class UsuarioViewSet(ViewSet):
    """View do usuário."""

    @ME
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
    )
    def me(self, request: Request) -> Response:
        """Retorna os dados do usuário autenticado."""
        usuario = UsuarioService.obter_usuario_por_rf_cpf(
            request.user.username,
        )
        response = UsuarioResponseSerializer(usuario).data

        return Response(
            response,
            status=status.HTTP_200_OK,
        )
