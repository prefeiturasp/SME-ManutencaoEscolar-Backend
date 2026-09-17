"""Filtros da API de Profissional."""

import django_filters

from .models import Profissional


class ProfissionalFilter(django_filters.FilterSet):
    """Filtra profissionais por nome, CPF, RG e status."""

    nome = django_filters.CharFilter(lookup_expr="icontains")
    cpf = django_filters.CharFilter(lookup_expr="icontains")
    rg = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter()

    class Meta:
        """Configuração do filtro de profissional."""

        model = Profissional
        fields = ["nome", "cpf", "rg", "status"]
