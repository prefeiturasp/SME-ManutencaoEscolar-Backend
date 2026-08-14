"""Filtros da API de Empresa."""

import django_filters

from .models import Empresa


class EmpresaFilter(django_filters.FilterSet):
    """Filtra empresas por nome, razão social, CNPJ e status."""

    nome = django_filters.CharFilter(lookup_expr="icontains")
    razao_social = django_filters.CharFilter(lookup_expr="icontains")
    cnpj = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter()

    class Meta:
        """Configuração do filtro de empresa."""

        model = Empresa
        fields = ["nome", "razao_social", "cnpj", "status"]
