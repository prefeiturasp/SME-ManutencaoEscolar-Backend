"""Filtros do domínio Serviço."""

from django_filters import rest_framework as filters

from apps.servico.models import Servico


def _converter_status(valor: str) -> bool:
    return valor == "true"


class ServicoFilter(filters.FilterSet):
    """Filtros disponíveis para Serviço."""

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

    class Meta:
        model = Servico
        fields = ["nome", "status"]
