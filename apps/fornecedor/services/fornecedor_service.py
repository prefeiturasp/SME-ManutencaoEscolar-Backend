"""Serviços de Fornecedor."""

from typing import Any

from apps.fornecedor.repository.fornecedor_repository import (
    FornecedorRepository,
)


class FornecedorService:
    """Orquestra as regras de negócio relacionadas a Fornecedor."""

    def __init__(self, repository: FornecedorRepository | None = None):
        """Inicializa o serviço com o repositório informado ou o padrão."""
        self.repository = repository or FornecedorRepository()

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria um fornecedor e retorna seus dados serializados."""
        return self.repository.criar(dados)
