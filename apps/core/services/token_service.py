"""Serviço para geração de tokens JWT e recuperação de senha."""

import logging

from django.db.models import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, Token

from apps.core.exceptions import TokenInvalidoError
from apps.core.repository.token_repository import TokenRepository
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.repository.usuario_repository import UsuarioRepository

logger = logging.getLogger(__name__)


class TokenService:
    """Responsável pela geração dos tokens JWT."""

    @classmethod
    def gerar_tokens(cls, id_usuario: int) -> dict[str, str | int]:
        """Gera tokens de acesso e refresh para um usuário.

        Este método atua como uma camada de serviço que delega a geração
        efetiva dos tokens para o TokenRepository.

        Args:
            id_usuario (int): ID do usuário autenticado que solicita os tokens.

        Returns:
            dict[str, str]: Dicionário contendo:
                - 'refresh': Token refresh para renovação de acesso
                - 'access': Token de acesso para autenticação nas requisições
        """
        return TokenRepository.gerar_tokens(id_usuario)

    @classmethod
    def atualizar_token(cls, refresh_token: Token) -> dict:
        """Valida um refresh token e verifica se o usuário associado existe.

        O método valida o refresh token informado e verifica se o usuário
        associado ao token ainda existe e está ativo. Caso o token seja
        inválido ou o usuário não seja encontrado, uma exceção é lançada.

        Args:
            refresh_token (Token): Refresh token enviado pelo cliente.

        Returns:
            dict[str, str]: Dicionário contendo o username do usuário.

        Raises:
            UsuarioNaoEncontradoError: Se o usuário associado ao token não
            existir ou estiver inativo.
            TokenError: Se o refresh token for inválido, expirado ou não puder
            ser validado.
        """
        try:
            refresh = RefreshToken(refresh_token)

            usuario_id = refresh["user_id"]

            return UsuarioRepository.retorna_username_usuario(usuario_id)

        except UsuarioNaoEncontradoError:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado.",
                detail="O token informado é inválido ou não está mais "
                "associado a um usuário válido.",
            ) from None
        except TokenError as exc:
            logger.error("Erro ao atulizar token: %s", exc)
            raise TokenInvalidoError(
                title="Token não atualizado.",
                detail="O refresh token é inválido ou já foi revogado.",
            ) from exc

    @classmethod
    def logout(cls, usuario_id: int, refresh_token: Token) -> None:
        """Realiza o logout do usuário revogando o refresh token.

        Valida se o refresh token pertence ao usuário autenticado e, em
        seguida, adiciona o token à blacklist para impedir sua reutilização
        na geração de novos access tokens.

        Args:
            usuario_id (int): Identificador do usuário autenticado.
            refresh_token (Token): Refresh token enviado pelo cliente.

        Raises:
            TokenInvalidoError: Se o refresh token for inválido, já tiver
                sido revogado ou não pertencer ao usuário autenticado.
        """
        try:
            token = RefreshToken(refresh_token)
            if int(token["user_id"]) != usuario_id:
                raise TokenInvalidoError(
                    title="Logout não realizado.",
                    detail="O token não pertence ao usuário autenticado.",
                )
            token.blacklist()
        except TokenError as exc:
            raise TokenInvalidoError(
                title="Logout não realizado.",
                detail="O refresh token é inválido ou já foi revogado.",
            ) from exc

    @classmethod
    def validar_token_recuperar_senha(cls, username: str, token: str) -> None:
        """Altera a senha de um usuário a partir de token de recuperação.

        Args:
            username (str): Nome de usuário (RF ou CPF) do usuário.
            token (str): Token de recuperação de senha enviado por e-mail.

        Raises:
            UsuarioNaoEncontradoError: Quando não existe usuário com o
                username.
            TokenRecuperacaoInvalidoError: Quando o token é inválido ou
                expirado.
        """
        try:
            TokenRepository.verificar_token_atualizar_senha(
                username=username,
                token=token,
            )
        except ObjectDoesNotExist:
            raise UsuarioNaoEncontradoError(
                title="Usuário não encontrado.",
                detail=("Usuário não encontrado ou inválido"),
            ) from None
        except TokenInvalidoError:
            raise TokenInvalidoError(
                title="O link está expirado!",
                detail="Por segurança, o link de redefinição tem validade de "
                "6 horas. Solicite um novo para redefinir sua senha.",
            ) from None
