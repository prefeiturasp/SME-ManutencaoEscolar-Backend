"""_summary_."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.serializers.usuario_serializer import (
    RecuperarSenhaSerializer,
)
from apps.usuarios.services.usuario_service import UsuarioService


class UsuarioViewSet(ViewSet):
    """View do usário."""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="recuperar-senha")
    def recuperar_senha(self, request: Request) -> Response:
        serializer = RecuperarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rf_ou_cpf = serializer.validated_data["registro_funcional_ou_cpf"]
        try:
            usuario = UsuarioService.obter_usuario_por_rf_cpf(rf_ou_cpf)
        except UsuarioNaoEncontradoError:
            return Response(
                {"detail": "Não existe usuário com este CPF ou RF"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"usuario": usuario})
