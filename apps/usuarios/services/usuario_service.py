"""Service do app usuarios."""

from typing import Any

from apps.usuarios.repository.cargo_repository import CargoEOLRepository
from apps.usuarios.repository.usuario_repository import UsuarioRepository


class UsuarioService:
    """Service responsável pelas regras de negócio do usuário."""

    @classmethod
    def sincronizar_usuario(
        cls,
        dados_usuario: dict[str, Any],
        dados_cargo: dict[str, Any],
    ) -> dict[str, Any]:
        """Sincroniza um usuário retornado pelo EOL."""
        try:
            codigo_cargo = int(dados_cargo["codigo_cargo"])
            cargo = CargoEOLRepository.buscar_por_codigo(codigo_cargo)
        except (TypeError, ValueError):
            # Essa parte é temporária, para conseguir logar enquanto não temos
            # usuários com cargos
            cargo = CargoEOLRepository.buscar_por_codigo(3360)

        if cargo is None:
            raise ValueError("Cargo não encontrado")

        return UsuarioRepository.atualizar_ou_criar(
            dados_usuario=dados_usuario,
            codigo_cargo=str(cargo["codigo"]),
        )
