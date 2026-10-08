"""Repositório do domínio Equipe."""

from typing import Any
from uuid import UUID

from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.profissional.models import Profissional
from apps.usuarios.models import Usuario


class EquipeRepository:
    """Encapsula a persistência de equipes e seus profissionais."""

    def existe_equipe(self, nome: str, empresa_uuid: UUID) -> bool:
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

    def existem_profissionais_inativos(self, uuids: list[UUID]) -> bool:
        """Verifica se há profissionais inativos entre os informados.

        Args:
            uuids: UUIDs dos profissionais.

        Returns:
            Verdadeiro quando ao menos um profissional está inativo.
        """
        return Profissional.objects.filter(
            uuid__in=uuids,
            status=False,
        ).exists()

    def obter_vinculos_com_equipes_ativas(
        self, uuids: list[UUID]
    ) -> list[tuple[UUID, str, str]]:
        """Obtém vínculos dos profissionais com equipes ativas.

        Args:
            uuids: UUIDs dos profissionais.

        Returns:
            UUID e nomes do profissional e da equipe para cada vínculo ativo.
        """
        return list(
            ProfissionalEquipe.objects.filter(
                profissional__uuid__in=uuids,
                equipe__situacao=True,
            ).values_list(
                "profissional__uuid",
                "profissional__nome",
                "equipe__nome",
            )
        )

    def criar(
        self,
        dados: dict[str, Any],
        profissionais: list[dict[str, Any]],
        usuario: Usuario,
    ) -> Equipe:
        """Cria uma equipe e os vínculos dos profissionais.

        Args:
            dados: Campos da equipe.
            profissionais: Profissionais e funções validados.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Equipe persistida.
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

        return equipe
