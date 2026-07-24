"""Repositório para gerenciamento de tokens JWT."""

from rest_framework_simplejwt.tokens import RefreshToken

from apps.usuarios.models.usuario import Usuario


class TokenRepository:
    """Repositório responsável pela geração de tokens de autenticação."""

    @classmethod
    def gerar_tokens(cls, usuario_id: int) -> dict[str, str]:
        """Gera um par de tokens (refresh e access) para um usuário específico.

        Args:
            usuario_id (int):  ID do usuário para o qual os tokens serão
                gerados.

        Returns:
            dict[str, str]:  Dicionário contendo os tokens 'refresh' e
                'access'.
        """
        usuario = Usuario.objects.get(pk=usuario_id)

        refresh = RefreshToken.for_user(usuario)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
