"""Repositório: único ponto de acesso ao ORM para o domínio Fornecedor."""

from typing import Any

from django.forms.models import model_to_dict

from apps.fornecedor.models import Fornecedor


class FornecedorRepository:
    """Encapsula todo acesso ao ORM referente a Fornecedor."""

    model = Fornecedor

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria um fornecedor e retorna seus dados em formato de dicionário."""
        fornecedor = self.model(**dados)
        fornecedor.full_clean()
        fornecedor.save()

        dados_fornecedor = model_to_dict(fornecedor)
        dados_fornecedor["id"] = fornecedor.id
        dados_fornecedor["uuid"] = str(fornecedor.uuid)
        return dados_fornecedor
