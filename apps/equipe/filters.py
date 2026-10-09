"""Filtros da API de Equipe."""

import django_filters

from .models import Equipe


class EquipeFilter(django_filters.FilterSet):
    """Filtra equipes por nome, empresa, lote e situacao."""

    nome = django_filters.CharFilter(lookup_expr="icontains")
    empresa = django_filters.CharFilter(
        field_name="empresa__uuid",
        lookup_expr="icontains",
    )
    lote = django_filters.CharFilter(
        field_name="lote__uuid",
        lookup_expr="icontains",
    )
    situacao = django_filters.BooleanFilter()

    class Meta:
        """Configuração do filtro de equipe."""

        model = Equipe
        fields = ["nome", "empresa", "lote", "situacao"]
