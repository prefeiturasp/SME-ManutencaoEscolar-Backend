"""Filtros do domínio Lote."""

from django_filters import rest_framework as filters

from apps.lote.models import Lote


def _converter_status(valor: str) -> bool:
    """Converta o status recebido como texto para booleano."""
    return valor == "true"


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    """Permite filtrar por múltiplos identificadores numéricos."""


class LoteFilter(filters.FilterSet):
    """Filtros disponíveis para Lote."""

    codigo_cadastro = filters.CharFilter(
        field_name="codigo_cadastro",
        lookup_expr="icontains",
    )

    nome = filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )

    status = filters.TypedChoiceFilter(
        field_name="status",
        choices=(
            ("true", "Ativo"),
            ("false", "Inativo"),
        ),
        coerce=_converter_status,
    )

    empresa = filters.NumberFilter(
        field_name="empresa_id",
    )

    diretorias_regionais = NumberInFilter(
        field_name=("vinculos_diretoria_regional__diretoria_regional_id"),
        lookup_expr="in",
        distinct=True,
    )

    periodo_inicial = filters.DateFilter(
        field_name="periodo_inicial",
        lookup_expr="gte",
    )

    periodo_final = filters.DateFilter(
        field_name="periodo_final",
        lookup_expr="lte",
    )

    class Meta:
        model = Lote
        fields = [
            "codigo_cadastro",
            "nome",
            "status",
            "empresa",
            "diretorias_regionais",
            "periodo_inicial",
            "periodo_final",
        ]
