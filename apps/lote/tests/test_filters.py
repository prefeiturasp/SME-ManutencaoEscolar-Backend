"""Testes dos filtros do domínio Lote."""

import pytest
from django_filters import rest_framework as filters

from apps.lote.filters import (
    LoteFilter,
    NumberInFilter,
    _converter_status,
)


@pytest.mark.parametrize(
    ("valor", "resultado_esperado"),
    [
        ("true", True),
        ("false", False),
    ],
)
def test_converte_status_para_booleano(
    valor: str,
    resultado_esperado: bool,
) -> None:
    """Deve converter o status textual para booleano.

    Args:
        valor: Status recebido como texto.
        resultado_esperado: Valor booleano esperado.
    """
    resultado = _converter_status(valor)

    assert resultado is resultado_esperado


def test_number_in_filter_herda_filtros_esperados() -> None:
    """Deve combinar os comportamentos de lista e número."""
    assert issubclass(NumberInFilter, filters.BaseInFilter)
    assert issubclass(NumberInFilter, filters.NumberFilter)


def test_configura_filtro_por_codigo_cadastro() -> None:
    """Deve configurar a busca parcial por código de cadastro."""
    filtro = LoteFilter.base_filters["codigo_cadastro"]

    assert isinstance(filtro, filters.CharFilter)
    assert filtro.field_name == "codigo_cadastro"
    assert filtro.lookup_expr == "icontains"


def test_configura_filtro_por_nome() -> None:
    """Deve configurar a busca parcial por nome."""
    filtro = LoteFilter.base_filters["nome"]

    assert isinstance(filtro, filters.CharFilter)
    assert filtro.field_name == "nome"
    assert filtro.lookup_expr == "icontains"


def test_configura_filtro_por_status() -> None:
    """Deve configurar o filtro de status como escolha tipada."""
    filtro = LoteFilter.base_filters["status"]

    assert isinstance(filtro, filters.TypedChoiceFilter)
    assert filtro.field_name == "status"
    assert filtro.lookup_expr == "exact"


def test_configura_filtro_por_empresa() -> None:
    """Deve configurar o filtro pelo identificador da empresa."""
    filtro = LoteFilter.base_filters["empresa"]

    assert isinstance(filtro, filters.NumberFilter)
    assert filtro.field_name == "empresa_id"
    assert filtro.lookup_expr == "exact"


def test_configura_filtro_por_diretorias_regionais() -> None:
    """Deve configurar o filtro por múltiplas Diretorias Regionais."""
    filtro = LoteFilter.base_filters["diretorias_regionais"]

    assert isinstance(filtro, NumberInFilter)
    assert filtro.field_name == (
        "vinculos_diretoria_regional__diretoria_regional_id"
    )
    assert filtro.lookup_expr == "in"
    assert filtro.distinct is True


def test_configura_filtro_por_periodo_inicial() -> None:
    """Deve configurar o limite inicial do período."""
    filtro = LoteFilter.base_filters["periodo_inicial"]

    assert isinstance(filtro, filters.DateFilter)
    assert filtro.field_name == "periodo_inicial"
    assert filtro.lookup_expr == "gte"


def test_configura_filtro_por_periodo_final() -> None:
    """Deve configurar o limite final do período."""
    filtro = LoteFilter.base_filters["periodo_final"]

    assert isinstance(filtro, filters.DateFilter)
    assert filtro.field_name == "periodo_final"
    assert filtro.lookup_expr == "lte"


def test_declara_todos_os_campos_disponiveis() -> None:
    """Deve declarar todos os campos disponíveis para filtragem."""
    campos_esperados = [
        "codigo_cadastro",
        "nome",
        "status",
        "empresa",
        "diretorias_regionais",
        "periodo_inicial",
        "periodo_final",
    ]

    assert LoteFilter.Meta.fields == campos_esperados
