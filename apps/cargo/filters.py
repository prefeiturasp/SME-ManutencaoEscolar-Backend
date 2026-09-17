"""Filtros do domínio Lote."""

from django_filters import rest_framework as filters

from apps.cargo.models import Cargo


def _converter_exige_documento(valor: str) -> bool:
    """Converta o exige_documento recebido como texto para booleano."""
    return valor == "true"


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    """Filtre por múltiplos valores numéricos."""

    pass


class CargoFilter(filters.FilterSet):
    """Filtros disponíveis para Cargo."""

    nome = filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )

    exige_documento = filters.TypedChoiceFilter(
        field_name="exige_documento",
        choices=(
            ("true", "Sim"),
            ("false", "Não"),
        ),
        coerce=_converter_exige_documento,
    )


    class Meta:
        model = Cargo
        fields = [
            "nome",
            "exige_documento"
        ]
