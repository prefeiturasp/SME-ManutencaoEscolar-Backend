"""Repositório de profissionais."""

from typing import Any

from apps.profissional.models import Profissional
from apps.usuarios.models import Usuario


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

    def atualizar(
        self, profissional: Profissional, dados: dict[str, Any]
    ) -> dict[str, Any]:
        """Atualiza e serializa um profissional.

        Args:
            profissional: Profissional que será atualizado.
            dados: Campos que devem ser aplicados ao profissional.

        Returns:
            Dados serializados do profissional atualizado.
        """
        for campo, valor in dados.items():
            setattr(profissional, campo, valor)
        profissional.full_clean()
        profissional.save()
        return self._serializar(profissional)

    def verificar_duplicidade(
        self,
        cpf: str | None,
        rg: str | None,
        profissional_ignorado: Profissional | None = None,
    ) -> dict[str, bool]:
        """Informa se CPF e RG já pertencem a outro profissional ativo.

        Args:
            cpf: CPF a ser verificado.
            rg: RG a ser verificado.
            profissional_ignorado: Profissional desconsiderado na consulta,
                usado na edição para ignorar o próprio registro.

        Returns:
            Dicionário com as chaves ``cpf`` e ``rg``, indicando se cada
            documento já pertence a outro profissional.
        """
        profissionais = self.model.objects.all()
        if profissional_ignorado is not None:
            profissionais = profissionais.exclude(pk=profissional_ignorado.pk)
        cpf_duplicado = bool(cpf) and profissionais.filter(cpf=cpf).exists()
        rg_duplicado = bool(rg) and profissionais.filter(rg=rg).exists()
        return {"cpf": cpf_duplicado, "rg": rg_duplicado}

    def deletar(
        self, profissional: Profissional, usuario: Usuario | None = None
    ) -> None:
        """
        Marca um profissional como deletado e registra o usuário.

        Args:
            profissional (Profissional): Instância do profissional a ser
                deletado.
            usuario (Usuario | None): Usuário que está realizando a deleção.
        """
        profissional.soft_delete(usuario=usuario)

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
