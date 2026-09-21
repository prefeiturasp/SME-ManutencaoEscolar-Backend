"""Repositório de funções profissionais."""

from typing import Any

from apps.profissional.models import FuncaoProfissional


class FuncaoProfissionalRepository:
    """Encapsula o acesso ao ORM referente às funções do profissional."""

    model = FuncaoProfissional

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria uma função do profissional.

        Args:
            dados: Dicionário contendo os dados da função a ser criada.

        Returns:
            Instância da função criada.
        """
        funcao = self.model(**dados)
        funcao.full_clean()
        funcao.save()
        return self._serializar(funcao)

    @staticmethod
    def _serializar(funcao: FuncaoProfissional) -> dict[str, Any]:
        """
        Retorna uma função persistida em formato de dicionário.

        Args:
            funcao: Instância do modelo `FuncaoProfissional` a ser serializada.

        Returns:
            Dicionário representando a função persistida.
        """
        return {
            "id": funcao.id,
            "uuid": str(funcao.uuid),
            "profissional": funcao.profissional,
            "cargo": funcao.cargo,
            "criado_por": funcao.criado_por,
            "criado_em": funcao.criado_em,
            "atualizado_por": funcao.atualizado_por,
            "atualizado_em": funcao.atualizado_em,
        }
