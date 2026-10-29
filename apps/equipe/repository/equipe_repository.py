"""Repositório do domínio Equipe."""

from typing import Any, cast
from uuid import UUID

from django.db import models

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

    def possui_vinculos_externos(self, equipe: Equipe) -> bool:
        """Verifica se a equipe é referenciada por outros cadastros.

        Considera qualquer modelo que aponte para a equipe, exceto os
        profissionais da própria equipe, que são removidos junto com ela.
        Registros excluídos logicamente não contam como vínculo.

        Args:
            equipe: Equipe que será verificada.

        Returns:
            Verdadeiro quando existe ao menos um vínculo ativo.
        """
        for relacao in Equipe._meta.related_objects:
            modelo = cast(type[models.Model], relacao.related_model)
            if modelo is ProfissionalEquipe:
                continue
            filtro = {relacao.field.name: equipe}
            if modelo._default_manager.filter(**filtro).exists():
                return True
        return False

    def deletar(
        self, equipe: Equipe, usuario: Usuario
    ) -> tuple[int, dict[str, int]]:
        """Exclui logicamente a equipe e os vínculos com seus profissionais.

        Args:
            equipe: Equipe que será excluída.
            usuario: Usuário responsável pela exclusão.

        Returns:
            Quantidade de registros afetados e o total por modelo.
        """
        for vinculo in ProfissionalEquipe.objects.filter(equipe=equipe):
            vinculo.soft_delete(usuario=usuario)
        return equipe.soft_delete(usuario=usuario)

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
            usuario: Usuário responsável pela atualização.

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
