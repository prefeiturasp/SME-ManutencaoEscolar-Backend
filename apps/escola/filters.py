"""Filtros do domínio Tipo de Escola."""

from django_filters import rest_framework as filters

from apps.escola.models import TipoEscola


class TipoEscolaFilter(filters.FilterSet):
    """Filtros disponíveis para tipos de escola."""

    sigla = filters.CharFilter(
        field_name="sigla",
        lookup_expr="icontains",
    )

    class Meta:
        model = TipoEscola
        fields = ["sigla"]
