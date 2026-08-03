"""Serviço para geração de tokens JWT."""

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, Token

from apps.core.repository.token_repository import TokenRepository
from apps.usuarios.exceptions import UsuarioNaoEncontradoError
from apps.usuarios.repository.usuario_repository import UsuarioRepository


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

        except TokenError:
            raise TokenError from None
