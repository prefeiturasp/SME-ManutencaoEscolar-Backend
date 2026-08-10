"""Repositório para gerenciamento de tokens JWT e recuperação de senha."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import TokenInvalidoError
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

    @classmethod
    def gerar_token_recuperar_senha(cls, username: str) -> dict:
        """Gera um token para recuperação de senha do usuário.

        Busca o usuário pelo nome de usuário e gera um token de recuperação
        de senha utilizando o ``PasswordResetTokenGenerator`` do Django.

        Args:
            username (str):  Nome de usuário utilizado para localizar o
                usuário que terá o token de recuperação gerado.


        Returns:
            dict: Dicionário contendo o token de recuperação na chave
                ``token_recuperacao``.
        """
        try:
            usuario = Usuario.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(usuario)
        return {"token_recuperacao": token}

    @classmethod
    def verificar_token_atualizar_senha(
        cls,
        username: str,
        token: str,
    ) -> None:
        """Altera a senha de um usuário a partir de token de recuperação.

        Args:
            username (str): Nome de usuário (RF ou CPF) do usuário.
            token (str): Token de recuperação de senha enviado por e-mail.

        Raises:
            TokenInvalidoError: Se o token for inválido ou expirado.
        """
        try:
            usuario = Usuario.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(usuario, token):
            raise TokenInvalidoError(
                title="Token inválido.",
                detail=(
                    "O token de recuperação de senha é inválido ou expirou."
                ),
            )

    @classmethod
    def invalidar_token_recuperacao_senha(
        cls, username: str, senha: str
    ) -> None:
        """Invalida o token de recuperação de senha do usuário.

        Atualiza a senha do usuário utilizando o mecanismo de hash do Django.
        A alteração do campo `password` faz com que tokens de recuperação
        previamente gerados pelo `PasswordResetTokenGenerator` deixem de ser
        válidos.

        Args:
            username (str): Nome de usuário utilizado para localizar o usuário.
            senha (str): Nova senha que será definida para o usuário.
        """
        try:
            usuario = Usuario.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None
        usuario.set_password(senha)
        usuario.save(update_fields=["password"])
