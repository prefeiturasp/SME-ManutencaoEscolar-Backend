"""Serviços gerais do domínio de solicitações de manutenção."""

from collections.abc import Sequence
from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone

from apps.solicitacao_manutencao.constants import SituacaoSolicitacao
from apps.solicitacao_manutencao.repositories.dre_repository import (
    SolicitacaoManutencaoDreRepository,
)
from apps.solicitacao_manutencao.repositories.solicitacao_repository import (
    SolicitacaoManutencaoBaseRepository,
)
from apps.solicitacao_manutencao.repositories.ue_repository import (
    SolicitacaoManutencaoUeRepository,
)
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import Usuario


def validar_situacao_editavel(
    solicitacao: dict[str, Any],
    situacoes_editaveis: Sequence[SituacaoSolicitacao],
) -> None:
    """Garante que a solicitação esteja em uma situação que permite edição.

    Args:
        solicitacao: Solicitação a ser validada.
        situacoes_editaveis: Situações em que a edição é permitida.

    Raises:
        ValidationError: Se a situação atual não permitir edição.
    """
    if solicitacao["situacao"] not in situacoes_editaveis:
        descricao = " ou ".join(
            situacao.label for situacao in situacoes_editaveis
        )
        raise ValidationError(
            {
                "situacao": (
                    "A solicitação só pode ser editada nessa situação. "
                    f"Precisa estar com a situação: {descricao}."
                )
            }
        )


def registrar_envio(
    dados: dict[str, Any], situacao: SituacaoSolicitacao
) -> dict[str, Any]:
    """Aplica a situação de destino e a data de envio aos dados.

    Args:
        dados: Dados da solicitação.
        situacao: Situação para a qual a solicitação será enviada.

    Returns:
        Novos dados com situação e data de envio preenchidas.
    """
    return {**dados, "situacao": situacao, "data_envio": timezone.now()}


class SolicitacaoManutencaoService:
    """Orquestra as operações gerais de solicitações de manutenção."""

    def __init__(
        self,
        repository: SolicitacaoManutencaoUeRepository | None = None,
        dre_repository: SolicitacaoManutencaoDreRepository | None = None,
    ) -> None:
        """Inicializa o serviço com os repositórios de solicitações.

        Args:
            repository: Repositório de solicitações de manutenção da UE.
            dre_repository: Repositório de solicitações de manutenção da DRE.
        """
        self.repository = repository or SolicitacaoManutencaoUeRepository()
        self.dre_repository = (
            dre_repository or SolicitacaoManutencaoDreRepository()
        )

    def _repository_por_usuario(
        self, usuario: Usuario | None
    ) -> SolicitacaoManutencaoBaseRepository:
        """Seleciona o repositório conforme o perfil do usuário.

        Args:
            usuario: Usuário autenticado.

        Returns:
            Repositório da DRE para perfil DRE; caso contrário, o da UE.
        """
        if usuario is not None and usuario.perfil == PerfilAcesso.DRE:
            return self.dre_repository
        return self.repository

    def listar_por_usuario(
        self, usuario: Usuario | None
    ) -> QuerySet[Any, dict[str, Any]]:
        """Lista solicitações visíveis ao usuário.

        Args:
            usuario: Usuário para o qual as solicitações serão listadas.
        Returns:
            Queryset de dicionários com dados resumidos.
        """
        return self._repository_por_usuario(usuario).listar_por_usuario(
            usuario
        )

    def get_detalhes_solicitacao(
        self, usuario: Usuario | None, uuid: str
    ) -> dict[str, Any] | None:
        """Retorna os detalhes de uma solicitação visível ao usuário.

        Args:
            usuario: Usuário responsável pela solicitação.
            uuid: UUID da solicitação.

        Returns:
            Dicionário com os detalhes ou ``None`` se não for encontrada.
        """
        return self._repository_por_usuario(usuario).get_detalhes_solicitacao(
            usuario, uuid
        )
