"""Repository de responsáveis de unidades educacionais."""

from typing import Any

from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


class ResponsavelUnidadeRepository:
    """Gerencia as operações de persistência de responsáveis."""

    model: type[ResponsavelUnidade] = ResponsavelUnidade
    historico_model: type[HistoricoResponsavel] = HistoricoResponsavel

    def buscar_por_registro_funcional(
        self,
        registro_funcional: str,
    ) -> dict[str, Any] | None:
        """Busca um responsável pelo registro funcional.

        A busca também retorna as unidades educacionais que possuem
        vínculo ativo com o responsável.

        Args:
            registro_funcional: Registro funcional ou CPF do responsável.

        Returns:
            Dicionário com os dados do responsável e suas unidades ativas,
            ou None quando o registro funcional não existir.
        """
        responsavel = self.model.objects.filter(
            registro_funcional=registro_funcional,
        ).first()

        if responsavel is None:
            return None

        historicos = self.historico_model.objects.filter(
            responsavel=responsavel,
            ativo=True,
        ).select_related("unidade_educacional")

        return {
            "uuid": str(responsavel.uuid),
            "registro_funcional": responsavel.registro_funcional,
            "nome": responsavel.nome,
            "unidades": [
                {
                    "id": historico.unidade_educacional.id,
                    "uuid": str(historico.unidade_educacional.uuid),
                    "codigo_eol": historico.unidade_educacional.codigo_eol,
                    "nome": historico.unidade_educacional.nome,
                }
                for historico in historicos
            ],
        }

    def existe_vinculo_ativo(
        self,
        unidade: Unidadeeducacional,
        responsavel_uuid: str,
    ) -> bool:
        """Verifica se o responsável possui vínculo ativo com a unidade.

        Args:
            unidade: Unidade educacional que será verificada.
            responsavel_uuid: UUID do responsável.

        Returns:
            True quando existir vínculo ativo; caso contrário, False.
        """
        return self.historico_model.objects.filter(
            responsavel__uuid=responsavel_uuid,
            unidade_educacional=unidade,
            ativo=True,
        ).exists()

    def buscar_vinculo_ativo(
        self,
        unidade: Unidadeeducacional,
        responsavel_uuid: str,
    ) -> HistoricoResponsavel:
        """Busca o vínculo ativo de um responsável com uma unidade.

        Args:
            unidade: Unidade educacional vinculada ao responsável.
            responsavel_uuid: UUID do responsável.

        Returns:
            Histórico ativo do responsável na unidade.
        """
        return self.historico_model.objects.select_related(
            "responsavel",
            "cargo",
        ).get(
            responsavel__uuid=responsavel_uuid,
            unidade_educacional=unidade,
            ativo=True,
        )

    def criar_vinculo(
        self,
        responsavel: ResponsavelUnidade,
        unidade: Unidadeeducacional,
        cargo: CargoEOL,
        usuario: Usuario | None,
    ) -> HistoricoResponsavel:
        """Cria o vínculo do responsável com uma unidade.

        Args:
            responsavel: Responsável que será vinculado.
            unidade: Unidade educacional.
            cargo: Cargo do responsável na unidade.
            usuario: Usuário responsável pela operação.

        Returns:
            Histórico criado para o responsável.
        """
        historico = self.historico_model(
            responsavel=responsavel,
            unidade_educacional=unidade,
            cargo=cargo,
            ativo=True,
            criado_por=usuario,
            atualizado_por=usuario,
        )

        historico.full_clean()
        historico.save()

        return historico

    def listar_vinculos_ativos(
        self,
        unidade: Unidadeeducacional,
    ) -> list[HistoricoResponsavel]:
        """Lista os responsáveis ativos vinculados à unidade.

        Args:
            unidade: Unidade educacional que será consultada.

        Returns:
            Lista de históricos ativos com responsável e cargo carregados.
        """
        return list(
            self.historico_model.objects.filter(
                unidade_educacional=unidade,
                ativo=True,
            ).select_related(
                "responsavel",
                "cargo",
            )
        )
