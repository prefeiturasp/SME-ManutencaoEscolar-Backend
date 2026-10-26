"""Serviços gerais do domínio de solicitações de manutenção."""

from typing import Any

from django.db.models import QuerySet

from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.repository import (
    SolicitacaoManutencaoRepository,
)
from apps.usuarios.models import Usuario


class SolicitacaoManutencaoService:
    """Orquestra as operações gerais de solicitações de manutenção."""

    def __init__(
        self,
        repository: SolicitacaoManutencaoRepository | None = None,
    ) -> None:
        """Inicializa o serviço com o repositório de solicitações.

        Args:
            repository: Repositório de solicitações de manutenção.
        """
        self.repository = repository or SolicitacaoManutencaoRepository()

    def listar_por_usuario(
        self,
        usuario: Usuario | None,
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Lista as solicitações visíveis para o usuário informado.

        Args:
            usuario: Usuário para o qual as solicitações serão listadas.

        Returns:
            Solicitações visíveis para o usuário.
        """
        return self.repository.listar_por_usuario(usuario)
