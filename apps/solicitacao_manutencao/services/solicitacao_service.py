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

    def buscar_por_usuario(
        self,
        usuario: Usuario | None,
        uuid: str | None = None,
    ) -> QuerySet[SolicitacaoManutencao, dict[str, Any]]:
        """Lista solicitações visíveis ou consulta uma pelo UUID.

        Args:
            usuario: Usuário para o qual as solicitações serão listadas.
            uuid: UUID opcional para consultar uma solicitação específica.

        Returns:
            Queryset de dicionários com dados resumidos ou detalhados.
        """
        return self.repository.buscar_por_usuario(usuario, uuid)
