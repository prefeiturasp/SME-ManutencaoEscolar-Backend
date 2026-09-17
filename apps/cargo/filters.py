"""Filtros do domínio Cargo."""

from django_filters import rest_framework as filters

from apps.cargo.models import Cargo

class CargoFilter(filters.FilterSet):
    """Filtros disponíveis para cargos."""

    nome = filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )
    exige_documento = filters.BooleanFilter(
        field_name="exige_documento",
    )

    class Meta:
        model = Cargo
        fields = ["nome", "exige_documento"]
