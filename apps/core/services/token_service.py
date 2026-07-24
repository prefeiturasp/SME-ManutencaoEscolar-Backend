"""Serviço para geração de tokens JWT."""

from apps.core.repository.token_repository import TokenRepository


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
