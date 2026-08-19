"""Repositório: único ponto de acesso ao ORM do domínio Responsável Técnico."""

from typing import Any

from django.forms.models import model_to_dict

from apps.empresa.models import ResponsavelTecnico


class ResponsavelTecnicoRepository:
    """Encapsula todo acesso ao ORM referente a Responsavel Técnico."""

    model = ResponsavelTecnico

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria um responsável técnico e retorna seus dados em dicionário."""
        responsavel = self.model(**dados)
        responsavel.save()

        return self._serializar(responsavel)

    def existe_por_empresa_e_tipo(self, empresa_id: int, tipo: str) -> bool:
        """Verifica se já existe responsável técnico do tipo na empresa."""
        return self.model.objects.filter(
            empresa_id=empresa_id, tipo=tipo
        ).exists()

    def _serializar(self, responsavel: ResponsavelTecnico) -> dict[str, Any]:
        """Serializa uma instância de Responsavel Técnico em dicionário."""
        dados_responsavel = model_to_dict(responsavel)
        dados_responsavel["id"] = responsavel.id
        dados_responsavel["uuid"] = str(responsavel.uuid)
        dados_responsavel["empresa"] = responsavel.empresa
        dados_responsavel["criado_por"] = responsavel.criado_por
        dados_responsavel["atualizado_por"] = responsavel.atualizado_por
        dados_responsavel["criado_em"] = responsavel.criado_em
        dados_responsavel["atualizado_em"] = responsavel.atualizado_em
        return dados_responsavel
