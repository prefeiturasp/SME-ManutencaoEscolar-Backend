"""_summary_."""

from apps.core.repository.token_repository import TokenRepository


class TokenService:
    """Responsável pela geração dos tokens JWT."""

    @classmethod
    def gerar_tokens(cls, id_usuario: int) -> dict[str, str]:
        return TokenRepository.gerar_tokens(id_usuario)
