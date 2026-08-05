"""_summary_."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.core.exceptions import EnvioEmailError
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
            UsuarioService.enviar_email_recuperacao_senha(usuario)
        except UsuarioNaoEncontradoError:
            return Response(
                {"detail": "Não existe usuário com este CPF ou RF"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except EnvioEmailError as exc:
            return Response(
                {"detail": exc.detail},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        parte_local, dominio = usuario["email"].rsplit("@", 1)
        quantidade_letras_visiveis = 3

        email_mascarado = (
            f"{parte_local[:quantidade_letras_visiveis]}"
            f"{'*' * (len(parte_local) - quantidade_letras_visiveis)}"
            f"@{dominio}"
        )

        return Response({"email": email_mascarado}, status=status.HTTP_200_OK)
