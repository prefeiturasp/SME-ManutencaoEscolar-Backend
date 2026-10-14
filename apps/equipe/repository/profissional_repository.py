"""Repositório dos vínculos de profissionais com equipes."""

from typing import Any
from uuid import UUID

from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.profissional.models import Profissional
from apps.usuarios.models import Usuario


class ProfissionalEquipeRepository:
    """Encapsula a persistência dos profissionais de uma equipe."""

    model = ProfissionalEquipe

    def criar(
        self, equipe: Equipe, dados: dict[str, Any], usuario: Usuario
    ) -> dict[str, Any]:
        """Cria um vínculo de profissional com equipe.

        Args:
            equipe: Equipe à qual o profissional será vinculado.
            dados: Profissional e função do vínculo.
            usuario: Usuário responsável pelo cadastro.

        Returns:
            Dicionário com os dados do vínculo criado.
        """
        vinculo = self.model(equipe=equipe, criado_por=usuario, **dados)
        vinculo.full_clean()
        vinculo.save()
        return self._serializar(vinculo)

    def atualizar(
        self,
        vinculo: ProfissionalEquipe,
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Atualiza um vínculo de profissional com equipe.

        Args:
            vinculo: Vínculo a ser atualizado.
            dados: Campos que devem ser aplicados à função.
            usuario: Usuário responsável pela atualização.

        Returns:
            Dicionário com os dados do vínculo atualizado.
        """
        campos = {**dados, "atualizado_por": usuario}
        campos_alterados = [
            campo
            for campo, valor in campos.items()
            if getattr(vinculo, campo) != valor
        ]
        for campo in campos_alterados:
            setattr(vinculo, campo, campos[campo])
        if campos_alterados:
            vinculo.full_clean()
            vinculo.save(update_fields=[*campos_alterados, "atualizado_em"])
        return self._serializar(vinculo)

    def listar_por_equipe(self, equipe: Equipe) -> list[ProfissionalEquipe]:
        """Lista os vínculos ativos de uma equipe.

        Args:
            equipe: Equipe cujos vínculos serão listados.

        Returns:
            Vínculos ativos da equipe.
        """
        return list(self.model.objects.filter(equipe=equipe))

    def existem_profissionais_inativos(self, uuids: list[UUID]) -> bool:
        """Verifica se há profissionais inativos entre os informados."""
        return Profissional.objects.filter(
            uuid__in=uuids, status=False
        ).exists()

    def obter_vinculos_com_equipes_ativas(
        self, uuids: list[UUID], equipe: Equipe | None = None
    ) -> list[tuple[UUID, str, str]]:
        """Obtém vínculos dos profissionais com outras equipes ativas."""
        vinculos = self.model.objects.filter(
            profissional__uuid__in=uuids, equipe__situacao=True
        )
        if equipe is not None:
            vinculos = vinculos.exclude(equipe=equipe)
        return list(
            vinculos.values_list(
                "profissional__uuid", "profissional__nome", "equipe__nome"
            )
        )

    def remover(
        self,
        vinculo: ProfissionalEquipe,
        usuario: Usuario | None = None,
    ) -> None:
        """Remove logicamente uma função profissional.

        Args:
            vinculo: Vínculo que será removido.
            usuario: Usuário responsável pela remoção.
        """
        vinculo.soft_delete(usuario=usuario)

    def _serializar(self, vinculo: ProfissionalEquipe) -> dict[str, Any]:
        """
        Serializa um vínculo de profissional com equipe.

        Args:
            vinculo: Vínculo a ser serializado.

        Returns:
            Dicionário com os dados do profissional serializado.

        """
        return {
            "uuid": vinculo.uuid,
            "profissional": {
                "uuid": vinculo.profissional.uuid,
                "nome": vinculo.profissional.nome,
            },
            "funcao": {
                "uuid": vinculo.funcao.uuid,
                "nome": vinculo.funcao.cargo.nome,
            },
        }
