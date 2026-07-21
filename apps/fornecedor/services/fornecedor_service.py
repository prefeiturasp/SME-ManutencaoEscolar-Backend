"""Serviços de Fornecedor."""

from typing import Any

from apps.fornecedor.models import Fornecedor
from apps.fornecedor.repository.fornecedor_repository import (
    FornecedorRepository,
)


class FornecedorNaoEncontradoError(Exception):
    """Levantada quando um fornecedor não é encontrado."""


class FornecedorCnpjDuplicadoError(Exception):
    """Levantada quando já existe um fornecedor com o mesmo CNPJ."""


class FornecedorService:
    """Orquestra as regras de negócio relacionadas a Fornecedor."""

    def __init__(self, repository: FornecedorRepository | None = None):
        self.repository = repository or FornecedorRepository()

    def criar(self, dados: dict[str, Any]) -> Fornecedor:
        return self.repository.create(dados)
