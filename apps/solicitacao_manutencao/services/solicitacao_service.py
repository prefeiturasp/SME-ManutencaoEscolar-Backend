"""Serviços gerais do domínio de solicitações de manutenção."""

from typing import Any

from django.db.models import QuerySet

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
        self, usuario: Usuario | None
    ) -> QuerySet[Any, dict[str, Any]]:
        """Lista solicitações visíveis ao usuário.

        Args:
            usuario: Usuário para o qual as solicitações serão listadas.
        Returns:
            Queryset de dicionários com dados resumidos.
        """
        return self.repository.listar_por_usuario(usuario)

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
        return self.repository.get_detalhes_solicitacao(usuario, uuid)
