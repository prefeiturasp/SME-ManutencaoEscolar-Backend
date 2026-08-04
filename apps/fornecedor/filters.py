"""Filtros da API de Fornecedor."""

import django_filters

from .models import Fornecedor


class FornecedorFilter(django_filters.FilterSet):
    """Filtra fornecedores por nome, razão social, CNPJ e status."""

    nome = django_filters.CharFilter(lookup_expr="icontains")
    razao_social = django_filters.CharFilter(lookup_expr="icontains")
    cnpj = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter()

    class Meta:
        """Configuração do filtro de fornecedor."""

        model = Fornecedor
        fields = ["nome", "razao_social", "cnpj", "status"]
