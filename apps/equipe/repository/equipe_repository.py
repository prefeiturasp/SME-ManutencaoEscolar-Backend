"""Repositório do domínio Equipe."""

from typing import Any
from uuid import UUID

from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.usuarios.models import Usuario


class EquipeRepository:
    """Encapsula a persistência de equipes e seus profissionais."""

    def existe_equipe_empresa(self, nome: str, empresa_uuid: UUID) -> bool:
        """Verifica se existe uma equipe com o mesmo nome na empresa.

        Args:
            nome: Nome da equipe.
            empresa_uuid: UUID da empresa.

        Returns:
            Verdadeiro quando uma equipe correspondente existe.
        """
        return Equipe.objects.filter(
            nome__iexact=nome,
            empresa__uuid=empresa_uuid,
        ).exists()

    def criar(
        self,
        dados: dict[str, Any],
        profissionais: list[dict[str, Any]],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria uma equipe.

        Args:
            dados: Campos da equipe.
            profissionais: Profissionais e funções da equipe.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dados da equipe persistida.
        """
        equipe = Equipe(**dados, criado_por=usuario)
        equipe.full_clean()
        equipe.save()

        for dados_profissional in profissionais:
            vinculo = ProfissionalEquipe(
                equipe=equipe,
                criado_por=usuario,
                **dados_profissional,
            )
            vinculo.full_clean()
            vinculo.save()

        return self._serializar(equipe)

    def atualizar(
        self, equipe: Equipe, dados: dict[str, Any], usuario: Usuario
    ) -> dict[str, Any]:
        """Atualiza uma equipe.

        Args:
            equipe: Equipe que será atualizada.
            dados: Campos que devem ser aplicados à equipe.

        Returns:
            Dados da equipe atualizada.
        """
        equipe.atualizado_por = usuario
        for campo, valor in dados.items():
            setattr(equipe, campo, valor)
        equipe.full_clean()
        equipe.save()
        return self._serializar(equipe)

    def _serializar(self, equipe: Equipe) -> dict[str, Any]:
        """Serializa uma equipe.

        Args:
            equipe: Instância da equipe a ser serializada.

        Returns:
            Dicionário representando a equipe.
        """
        return {
            "uuid": str(equipe.uuid),
            "nome": equipe.nome,
            "empresa": equipe.empresa if equipe.empresa else None,
            "lote": equipe.lote if equipe.lote else None,
            "situacao": equipe.situacao,
            "criado_por": equipe.criado_por if equipe.criado_por else None,
            "atualizado_por": (
                equipe.atualizado_por if equipe.atualizado_por else None
            ),
            "criado_em": equipe.criado_em.isoformat(),
            "atualizado_em": (
                equipe.atualizado_em.isoformat()
                if equipe.atualizado_em
                else None
            ),
        }
