"""Filtros do domínio Tipo de Escola."""

import django_filters
from django.db.models import QuerySet

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
    diretoria_regional = django_filters.NumberFilter(
        field_name="diretoria_regional__id",
        lookup_expr="exact",
    )

    class Meta:
        model = Subprefeitura
        fields = ("codigo_eol", "nome", "diretoria_regional")


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
    subprefeitura = django_filters.CharFilter(
        method="filtrar_subprefeitura",
    )
    status = django_filters.BooleanFilter(
        field_name="status",
        lookup_expr="exact",
    )
    lote = django_filters.CharFilter(
        field_name="diretoria_regional__vinculo_lote__lote__nome",
        lookup_expr="icontains",
    )

    def filtrar_subprefeitura(
        self,
        queryset: QuerySet[Unidadeeducacional],
        name: str,
        value: str,
    ) -> QuerySet[Unidadeeducacional]:
        """Filtra unidades educacionais por subprefeitura.

        Permite filtrar pelas unidades vinculadas a uma subprefeitura
        específica ou pelas unidades que não possuem subprefeitura.

        Args:
            queryset: QuerySet de unidades educacionais a ser filtrado.
            name: Nome do campo utilizado pelo filtro.
            value: UUID da subprefeitura ou o valor
                ``"sem-subprefeitura"`` para unidades sem subprefeitura.

        Returns:
            QuerySet contendo as unidades educacionais que atendem
            ao critério de subprefeitura informado.
        """
        if value == "sem-subprefeitura":
            return queryset.filter(subprefeitura__isnull=True)

        return queryset.filter(subprefeitura__uuid=value)

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
