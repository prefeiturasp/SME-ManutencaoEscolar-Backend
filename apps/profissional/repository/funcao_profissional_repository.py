"""Repositório de funções profissionais."""

from typing import Any

from apps.profissional.models import FuncaoProfissional
from apps.usuarios.models import Usuario


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

    def atualizar(
        self, funcao: FuncaoProfissional, dados: dict[str, Any]
    ) -> dict[str, Any]:
        """Atualiza e serializa uma função profissional.

        Args:
            funcao: Função profissional que será atualizada.
            dados: Campos que devem ser aplicados à função.

        Returns:
            Dados serializados da função atualizada.
        """
        campos = {**dados}
        campos.pop("uuid", None)
        campos_alterados = [
            campo
            for campo, valor in campos.items()
            if getattr(funcao, campo) != valor
        ]
        for campo in campos_alterados:
            setattr(funcao, campo, campos[campo])
        if campos_alterados:
            funcao.full_clean()
            funcao.save(update_fields=[*campos_alterados, "atualizado_em"])
        return self._serializar(funcao)

    def listar_por_profissional(
        self, profissional_id: int
    ) -> list[FuncaoProfissional]:
        """Lista as funções ativas de um profissional.

        Args:
            profissional_id: ID do profissional dono das funções.

        Returns:
            Funções ativas vinculadas ao profissional.
        """
        return list(self.model.objects.filter(profissional_id=profissional_id))

    def remover(
        self,
        funcao: FuncaoProfissional,
        usuario: Usuario | None = None,
    ) -> None:
        """Remove logicamente uma função profissional.

        Args:
            funcao: Função profissional que será removida.
            usuario: Usuário responsável pela remoção.
        """
        funcao.soft_delete(usuario=usuario)

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
