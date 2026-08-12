"""Repositório de serviços."""

from typing import Any
from uuid import UUID

from apps.servico.models import Servico


class ServicoRepository:
    """Gerencia operações de persistência de serviços."""

    model: type[Servico] = Servico

    def existe_por_nome(
        self,
        nome: str,
        excluir_uuid: UUID | None = None,
    ) -> bool:
        """Verifica se existe serviço cadastrado com o mesmo nome."""
        queryset = self.model.objects.filter(nome__iexact=nome)

        if excluir_uuid is not None:
            queryset = queryset.exclude(uuid=excluir_uuid)

        return queryset.exists()

    def criar(self, dados: dict[str, Any], usuario_id: int) -> Servico:
        """Cria e persiste um serviço."""
        servico = self.model(
            **dados,
            criado_por_id=usuario_id,
            atualizado_por_id=usuario_id
            )
        servico.full_clean()
        servico.save()

        return servico

    def atualizar(
        self,
        servico: Servico,
        dados: dict[str, Any],
        usuario_id: int,
    ) -> Servico:
        """Atualiza e persiste um serviço existente."""
        if "nome" in dados:
            servico.nome = dados["nome"]

        if "status" in dados:
            servico.status = dados["status"]

        servico.atualizado_por_id = usuario_id

        servico.full_clean()
        servico.save()

        return servico