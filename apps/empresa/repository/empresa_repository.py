"""Repositório: único ponto de acesso ao ORM para o domínio Empresa."""

from typing import Any

from django.forms.models import model_to_dict

from apps.empresa.models import Empresa


class EmpresaRepository:
    """Encapsula todo acesso ao ORM referente a Empresa."""

    model = Empresa

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria uma empresa e retorna seus dados em formato de dicionário."""
        empresa = self.model(**dados)
        empresa.full_clean()
        empresa.save()

        dados_empresa = model_to_dict(empresa)
        dados_empresa["id"] = empresa.id
        dados_empresa["uuid"] = str(empresa.uuid)
        return dados_empresa
