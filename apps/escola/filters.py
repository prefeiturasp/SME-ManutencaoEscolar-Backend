"""Filtros do domínio Tipo de Escola."""

import django_filters

from apps.escola.models import (
    DiretoriaRegional,
    Subprefeitura,
    TipoEscola,
    Unidadeeducacional,
)


class TipoEscolaFilter(django_filters.FilterSet):
    """Filtros disponíveis para tipos de escola."""

    sigla = django_filters.CharFilter(
        field_name="sigla",
        lookup_expr="icontains",
    )

    class Meta:
        model = TipoEscola
        fields = ["sigla"]


class SubprefeituraFilter(django_filters.FilterSet):
    """Filtros disponíveis para subprefeituras."""

    codigo_eol = django_filters.CharFilter(
        field_name="codigo_eol",
        lookup_expr="exact",
    )
    nome = django_filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )

    class Meta:
        model = Subprefeitura
        fields = (
            "codigo_eol",
            "nome",
        )


class DiretoriaRegionalFilter(django_filters.FilterSet):
    """Filtros disponíveis para diretorias regionais."""

    codigo = django_filters.CharFilter(
        field_name="codigo",
        lookup_expr="exact",
    )
    nome = django_filters.CharFilter(
        field_name="nome",
        lookup_expr="icontains",
    )
    abreviacao = django_filters.CharFilter(
        field_name="abreviacao",
        lookup_expr="icontains",
    )

    class Meta:
        model = DiretoriaRegional
        fields = ("codigo", "nome", "abreviacao")


class UnidadeEducacionalFilter(django_filters.FilterSet):
    """Filtros disponíveis para unidades educacionais."""

    codigo_eol = django_filters.CharFilter(
        field_name="codigo_eol",
        lookup_expr="exact",
    )
    tipo_escola = django_filters.UUIDFilter(
        field_name="tipo_escola__uuid",
        lookup_expr="exact",
    )
    diretoria_regional = django_filters.NumberFilter(
        field_name="diretoria_regional__id",
        lookup_expr="exact",
    )
    unidade_educacional = django_filters.UUIDFilter(
        field_name="uuid",
        lookup_expr="exact",
    )
    subprefeitura = django_filters.UUIDFilter(
        field_name="subprefeitura__uuid",
        lookup_expr="exact",
    )
    status = django_filters.BooleanFilter(
        field_name="status",
        lookup_expr="exact",
    )
    lote = django_filters.CharFilter(
        field_name="diretoria_regional__vinculo_lote__lote__codigo_cadastro",
        lookup_expr="icontains",
    )

    class Meta:
        model = Unidadeeducacional
        fields = (
            "codigo_eol",
            "tipo_escola",
            "diretoria_regional",
            "unidade_educacional",
            "subprefeitura",
            "lote",
            "status",
        )
