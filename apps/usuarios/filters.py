"""Filtros disponíveis do app usuarios."""

import django_filters

from apps.usuarios.models.cargo_eol import CargoEOL


class CargoEOLFilter(django_filters.FilterSet):
    """Define os critérios de filtragem disponíveis para cargos EOL.

    Permite restringir a consulta de cargos pelos seguintes critérios:
        - ``codigo``: código exato do cargo EOL.
        - ``nome``: parte do nome do cargo, sem distinção entre maiúsculas
        e minúsculas.
        - ``perfil``: perfil de acesso associado ao cargo.
        - ``ativo``: situação do cargo, permitindo consultar cargos ativos
        ou inativos.
    """

    codigo = django_filters.CharFilter(
        field_name="codigo",
        lookup_expr="exact",
    )
    nome = django_filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )
    perfil = django_filters.CharFilter(
        field_name="perfil",
        lookup_expr="exact",
    )
    ativo = django_filters.BooleanFilter(
        field_name="ativo",
        lookup_expr="exact",
    )

    class Meta:
        model = CargoEOL
        fields = (
            "codigo",
            "nome",
            "perfil",
            "ativo",
        )
