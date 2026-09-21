"""Repositório de profissionais."""

from typing import Any

from apps.profissional.models import Profissional


class ProfissionalRepository:
    """Encapsula o acesso ao ORM referente a profissionais."""

    model = Profissional

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria e serializa um profissional.

        Args:
            dados: Dicionário contendo os dados do profissional a ser criado.

        Returns:
            Instância do profissional criado.
        """
        profissional = self.model(**dados)
        profissional.full_clean()
        profissional.save()
        return self._serializar(profissional)

    @staticmethod
    def _serializar(profissional: Profissional) -> dict[str, Any]:
        """
        Retorna um profissional persistido em formato de dicionário.

        Args:
            profissional: Instância do modelo `Profissional` a ser serializada.

        Returns:
            Dicionário representando o profissional persistido.
        """
        return {
            "id": profissional.id,
            "uuid": str(profissional.uuid),
            "nome": profissional.nome,
            "rg": profissional.rg,
            "cpf": profissional.cpf,
            "status": profissional.status,
            "criado_por": profissional.criado_por_id,
            "criado_em": profissional.criado_em,
            "atualizado_por": profissional.atualizado_por_id,
            "atualizado_em": profissional.atualizado_em,
        }
