"""Repositório: único ponto de acesso ao ORM para o domínio Fornecedor."""

from typing import Any

from apps.fornecedor.models import Fornecedor


class FornecedorRepository:
    """Encapsula todo acesso ao ORM referente a Fornecedor."""

    model = Fornecedor

    def create(self, dados: dict[str, Any]) -> Fornecedor:
        fornecedor = self.model(**dados)
        fornecedor.full_clean()
        fornecedor.save()
        return fornecedor
