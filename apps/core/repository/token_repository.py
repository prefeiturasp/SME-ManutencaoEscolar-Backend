"""_summary_."""

from rest_framework_simplejwt.tokens import RefreshToken

from apps.usuarios.models.usuario import Usuario


class TokenRepository:
    """_summary_."""

    @classmethod
    def gerar_tokens(cls, usuario_id: int) -> dict[str, str]:
        usuario = Usuario.objects.get(pk=usuario_id)

        refresh = RefreshToken.for_user(usuario)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
