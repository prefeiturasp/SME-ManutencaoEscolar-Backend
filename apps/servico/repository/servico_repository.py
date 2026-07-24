"""Repositório de Serviço."""

from typing import Any

from django.forms.models import model_to_dict

from apps.servico.models import Servico


class ServicoRepository:
    """Gerencia operações de persistência de Serviço."""

    model = Servico

    def existe_por_nome(self, nome: str) -> bool:
        """Verifica se existe serviço cadastrado com o mesmo nome."""
        return self.model.objects.filter(nome__iexact=nome).exists()

    def criar(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria e serializa um serviço."""
        servico = self.model(**dados)
        servico.full_clean()
        servico.save()

        dados_servico = model_to_dict(servico)
        dados_servico["id"] = servico.id
        dados_servico["uuid"] = str(servico.uuid)

        return dados_servico
