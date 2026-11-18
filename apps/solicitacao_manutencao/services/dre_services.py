"""Serviços do domínio de solicitações de manutenção operados pela DRE."""

from typing import Any

from apps.solicitacao_manutencao.constants import (
    MSG_SOLICITACAO_APROVADA_DRE,
    DecisaoAnaliseDre,
)
from apps.solicitacao_manutencao.models import (
    SituacaoSolicitacao,
)
from apps.solicitacao_manutencao.repositories.dre_repository import (
    SolicitacaoManutencaoDreRepository,
)
from apps.solicitacao_manutencao.services.solicitacao_service import (
    registrar_envio,
    validar_situacao_editavel,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoDreService:
    """Orquestra a análise de solicitações de manutenção pela DRE."""

    def __init__(
        self,
        repository: SolicitacaoManutencaoDreRepository | None = None,
    ) -> None:
        """Inicializa o serviço com suas dependências.

        Args:
            repository: Repositório de solicitações de manutenção.
        """
        self.repository = repository or SolicitacaoManutencaoDreRepository()

    def atualizar(
        self,
        solicitacao: dict[str, Any],
        dados: dict[str, Any],
        usuario: Usuario,
        enviar: bool = False,
    ) -> dict[str, Any]:
        """Atualiza uma solicitação por UUID.

        Args:
            solicitacao: Solicitação a ser atualizada.
            dados: Dados validados da solicitação e de seus serviços.
            usuario: Usuário responsável pela atualização.
            enviar: Indica se a solicitação deve ser enviada para a DRE.

        Returns:
            Dicionário com os dados da análise registrada (`analise`) e a
            mensagem de confirmação (`mensagem`), preenchida somente quando
            a solicitação é aprovada e enviada.
        """
        validar_situacao_editavel(
            solicitacao, [SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE]
        )

        if enviar:
            dados = registrar_envio(
                dados, SituacaoSolicitacao.AGUARDANDO_ANALISE_GME_SME
            )

        analise = self.repository.atualizar(solicitacao, dados, usuario)
        mensagem = None
        if enviar and analise["decisao"] == DecisaoAnaliseDre.APROVADA:
            mensagem = MSG_SOLICITACAO_APROVADA_DRE.format(
                codigo=solicitacao["codigo"]
            )
        return {"analise": analise, "mensagem": mensagem}
