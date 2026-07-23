"""_summary_."""

from typing import Any

from apps.usuarios.repository.cargo_repository import CargoEOLRepository
from apps.usuarios.repository.usuario_repository import UsuarioRepository


class UsuarioService:
    """Service responsável pelas regras de negócio do usuário."""

    @classmethod
    def sincronizar_usuario(
        cls,
        *,
        nome: str,
        email: str | None,
        registro_funcional: str | None,
        cpf: str | None,
        dados_cargo: dict[str, Any],
    ) -> dict[str, Any]:
        """Sincroniza um usuário retornado pelo EOL."""
        cargo = CargoEOLRepository.buscar_por_codigo(
            dados_cargo["codigo_cargo"]
        )
        if cargo is None:
            raise ValueError("Cargo não encontrado")

        return UsuarioRepository.atualizar_ou_criar(
            nome=nome,
            email=email or "",
            registro_funcional=registro_funcional,
            cpf=cpf,
            codigo_cargo=cargo["codigo"],
        )
