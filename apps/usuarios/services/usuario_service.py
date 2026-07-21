"""_summary_."""

from apps.usuarios.models import CargoEOL
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
        codigo_cargo: int,
        nome_cargo: str,
    ) -> dict:
        """Sincroniza um usuário retornado pelo EOL."""
        cargo, _ = CargoEOL.objects.get_or_create(
            codigo=codigo_cargo,
            defaults={
                "nome": nome_cargo,
            },
        )

        return UsuarioRepository.atualizar_ou_criar(
            nome=nome,
            email=email or "",
            registro_funcional=registro_funcional,
            cpf=cpf,
            cargo=cargo,
        )
