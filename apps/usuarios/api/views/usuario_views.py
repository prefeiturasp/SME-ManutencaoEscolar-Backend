"""View responsável pelos endpoints relacionados ao usuário.

Disponibiliza endpoints para consulta dos dados do usuário autenticado.
"""

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
    """Disponibiliza endpoints relacionados ao usuário autenticado."""

    @ME
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
    )
    def me(self, request: Request) -> Response:
        """Retorna os dados do usuário autenticado.

        O usuário é identificado a partir do RF ou CPF informado no
        ``username`` do usuário autenticado e seus dados são serializados
        para a resposta da API.

        Args:
            request (Request): Requisição contendo os dados do usuário
                autenticado.

        Returns:
            Response: Resposta HTTP contendo os dados do usuário autenticado.
        """
        usuario = UsuarioService.obter_usuario_por_rf_cpf(
            request.user.username,
        )
        response = UsuarioResponseSerializer(usuario).data

        return Response(
            response,
            status=status.HTTP_200_OK,
        )
