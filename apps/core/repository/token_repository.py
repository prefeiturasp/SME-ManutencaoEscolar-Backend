"""Repositório para gerenciamento de tokens JWT e recuperação de senha.

Este módulo centraliza a geração de tokens JWT utilizados na autenticação dos
usuários e a geração e validação de tokens temporários para recuperação de
senha.
"""

from datetime import timedelta
from typing import cast

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import TokenInvalidoError
from apps.usuarios.models.usuario import Usuario
from config import settings


class TokenRepository:
    """Centraliza operações relacionadas aos tokens de usuários.

    O repositório disponibiliza dois mecanismos distintos de token:

        * tokens JWT ``access`` e ``refresh`` para autenticação;
        * tokens de recuperação de senha gerados pelo mecanismo padrão do
          Django.

    Os tokens JWT são gerados utilizando :class:`RefreshToken` do
    ``rest_framework_simplejwt`` e têm seus tempos de expiração definidos pelas
    configurações ``ACCESS_TOKEN_LIFETIME`` e ``REFRESH_TOKEN_LIFETIME`` de
    ``SIMPLE_JWT``.

    Os tokens de recuperação de senha são gerados e validados por meio de
    :class:`PasswordResetTokenGenerator`.
    """

    @classmethod
    def _consulta_por_username(cls, username: str) -> Usuario:
        """Recupera um usuário pelo username.

        Args:
            username (str): Nome de usuário utilizado para localizar
                o usuário.

        Returns:
            Usuario: Usuário encontrado.

        Raises:
            ObjectDoesNotExist: Quando não existe usuário com o
                username informado.
        """
        try:
            return Usuario.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist from None

    @classmethod
    def gerar_tokens(cls, usuario_id: int) -> dict[str, str | int]:
        """Gera os tokens JWT de acesso e renovação para um usuário.

        Cria um token ``refresh`` para o usuário informado e, a partir dele,
        gera o respectivo token ``access``.

        Além dos tokens, retorna os tempos de expiração configurados para cada
        tipo de token em segundos.

        Args:
            usuario_id (int):  Identificador do usuário para o qual os tokens
                serão gerados.

        Returns:
            dict[str, str]:  Dicionário contendo:
                - ``refresh``: Token JWT utilizado para renovação da
                    autenticação.
                - ``access``: Token JWT utilizado para autenticar requisições.
                - ``access_expires_in``: Tempo de validade do token de acesso,
                    em segundos.
                - ``refresh_expires_in``: Tempo de validade do token de
                    renovação, em segundos.
        """
        usuario = Usuario.objects.get(pk=usuario_id)

        refresh = RefreshToken.for_user(usuario)

        access_expira_em: timedelta = cast(
            timedelta, settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        )
        refresh_expira_em: timedelta = cast(
            timedelta, settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        )

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "access_expires_in": int(access_expira_em.total_seconds()),
            "refresh_expires_in": int(refresh_expira_em.total_seconds()),
        }

    @classmethod
    def gerar_token_recuperar_senha(cls, username: str) -> dict[str, str]:
        """Gera um token para recuperação de senha do usuário.

        Busca o usuário pelo nome de usuário e gera um token de recuperação
        de senha utilizando o ``PasswordResetTokenGenerator`` do Django.

        O token gerado é vinculado ao estado atual do usuário e deve ser
        posteriormente validado por :meth:`verificar_token_atualizar_senha`.

        Args:
            username (str):  Nome de usuário utilizado para localizar o
                usuário que terá o token de recuperação gerado.

        Returns:
            dict[str, str]: Dicionário contendo o token de recuperação na chave
                ``token_recuperacao``.
        """
        usuario = cls._consulta_por_username(username)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(usuario)
        return {"token_recuperacao": token}

    @classmethod
    def verificar_token_atualizar_senha(
        cls,
        username: str,
        token: str,
    ) -> None:
        """Valida um token de recuperação de senha..

        Localiza o usuário pelo nome de usuário e verifica se o token de
        recuperação ainda é válido e não expirou.

        Apesar do nome do método, esta operação **não altera a senha do
        usuário**. Ela apenas valida o token. A alteração efetiva da senha
        deve ser realizada pela camada responsável por essa operação após a
        validação bem-sucedida.

        A validade do token é determinada pelo
        :class:`PasswordResetTokenGenerator` do Django

        Args:
            username (str): Nome de usuário (RF ou CPF) do usuário.
            token (str): Token de recuperação de senha enviado por e-mail.

        Raises:
            TokenInvalidoError: Se o token for inválido ou expirado.
        """
        usuario = cls._consulta_por_username(username)
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(usuario, token):
            raise TokenInvalidoError(
                title="Token inválido.",
                detail=(
                    "O token de recuperação de senha é inválido ou expirou."
                ),
            )
