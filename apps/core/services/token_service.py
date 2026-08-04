"""Serviço para geração de tokens JWT."""

import logging

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
    def gerar_tokens(cls, id_usuario: int) -> dict[str, str]:
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
    def atualizar_token(cls, refresh_token: Token) -> None:
        """Valida um refresh token e verifica se o usuário associado existe.

        O método valida o refresh token informado e verifica se o usuário
        associado ao token ainda existe e está ativo. Caso o token seja
        inválido ou o usuário não seja encontrado, uma exceção é lançada.

        Args:
            refresh_token (Token): Refresh token enviado pelo cliente.

        Raises:
            UsuarioNaoEncontradoError: Se o usuário associado ao token não
            existir ou estiver inativo.
            TokenError: Se o refresh token for inválido, expirado ou não puder
            ser validado.
        """
        try:
            refresh = RefreshToken(refresh_token)

            usuario_id = refresh["user_id"]

            usuario = UsuarioRepository.usuario_existe_por_id(usuario_id)

            if usuario is False:
                raise UsuarioNaoEncontradoError(
                    title="Falha ao atualizar o token",
                    detail="O token informado é inválido ou não está mais "
                    "associado a um usuário válido.",
                )

        except TokenError as exc:
            logger.error("Erro ao atulizar token: %s", exc)
            raise TokenError from None

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
            usuario = UsuarioRepository.usuario_existe_por_id(usuario_id)

            if int(token["user_id"]) != usuario_id or usuario is False:
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
