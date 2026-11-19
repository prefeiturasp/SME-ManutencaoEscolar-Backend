"""Repositórios do domínio de solicitações de manutenção."""

from typing import Any, cast

from django.db import transaction
from django.db.models import QuerySet

from apps.solicitacao_manutencao.constants import SituacaoSolicitacao
from apps.solicitacao_manutencao.models import (
    HistoricoAnaliseSolicitacao,
    SolicitacaoManutencao,
)
from apps.solicitacao_manutencao.repositories.solicitacao_repository import (
    SolicitacaoManutencaoBaseRepository,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoDreRepository(SolicitacaoManutencaoBaseRepository):
    """Gerencia a persistência de solicitações de manutenção pela DRE."""

    campos_analise = ("decisao", "observacoes")

    def listar_por_usuario(
        self, usuario: Usuario | None
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Lista solicitações aguardando análise da DRE do usuário.

        Args:
            usuario: Usuário DRE responsável pela análise.

        Returns:
            Queryset de dicionários com dados resumidos.
        """
        if usuario is None or usuario.diretoria_regional_id is None:
            queryset = self.model.objects.none()
        else:
            queryset = self.model.objects.filter(
                unidade_educacional__diretoria_regional_id=(
                    usuario.diretoria_regional_id
                ),
                situacao=SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE,
            )

        return cast(
            QuerySet[SolicitacaoManutencao, dict[str, Any]],
            queryset.values(*self.campos_listagem),
        )

    @transaction.atomic
    def aprovar(
        self,
        solicitacao: dict[str, Any],
        dados: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Aprova uma solicitação e registra a análise da DRE.

        Args:
            solicitacao: Dados da solicitação a aprovar.
            dados: Campos da solicitação e da análise já validados.
            usuario: Usuário responsável pela aprovação.

        Returns:
            Dados da análise registrada.
        """
        dados_analise = {
            campo: dados[campo]
            for campo in self.campos_analise
            if campo in dados
        }
        dados_solicitacao = {
            campo: valor
            for campo, valor in dados.items()
            if campo not in self.campos_analise
        }
        self._atualizar_campos(solicitacao, dados_solicitacao, usuario)
        return self.criar_historico_analise(
            solicitacao, dados_analise, usuario
        )

    def criar_historico_analise(
        self,
        solicitacao: dict[str, Any],
        dados_analise: dict[str, Any],
        usuario: Usuario,
    ) -> dict[str, Any]:
        """Cria o histórico de análise da solicitação.

        Args:
            solicitacao: Dados da solicitação.
            dados_analise: Dados da análise.
            usuario: Usuário responsável pela criação do histórico.

        Returns:
            Dados do histórico de análise criado.
        """
        historico = HistoricoAnaliseSolicitacao.objects.create(
            solicitacao_manutencao_id=solicitacao["id"],
            **dados_analise,
            usuario=usuario,
            criado_por=usuario,
        )
        return self._serializar(historico)

    def _serializar(
        self, analise: HistoricoAnaliseSolicitacao
    ) -> dict[str, Any]:
        """Serializa uma análise de solicitação.

        Args:
            analise: Instância da análise.

        Returns:
            Dicionário com os dados da análise.
        """
        return {
            "id": analise.id,
            "uuid": str(analise.uuid),
            "usuario": analise.usuario_id,
            "decisao": analise.decisao,
            "observacoes": analise.observacoes,
            "data_alteracao": analise.data_alteracao,
            "criado_em": analise.criado_em,
        }
