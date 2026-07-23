"""_summary_."""

from typing import Any

from apps.usuarios.models import CargoEOL


class CargoEOLRepository:
    """Repositório responsável pelas operações de acesso aos cargos do EOL."""

    @classmethod
    def buscar_por_codigo(cls, codigo: int) -> dict[str, Any] | None:
        """
        Busca um cargo pelo seu código.

        Args:
            codigo: Código do cargo no EOL.

        Returns:
            dict[str, Any] | None: Dicionário contendo os dados do cargo,
            caso encontrado, ou ``None`` caso não exista.
        """
        cargo = CargoEOL.objects.filter(codigo=codigo).first()

        if cargo is None:
            return None

        return {
            "id": cargo.id,
            "codigo": cargo.codigo,
            "nome": cargo.nome,
            "perfil": cargo.perfil,
            "ativo": cargo.ativo,
        }
