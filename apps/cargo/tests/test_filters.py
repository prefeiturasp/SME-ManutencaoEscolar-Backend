"""Testes dos filtros do domínio de cargos."""

import pytest

from apps.cargo.filters import CargoFilter
from apps.cargo.models import Cargo


@pytest.mark.django_db
def test_filtrar_cargos_por_nome_parcial() -> None:
    """Adiciona à consulta uma busca parcial pelo nome."""
    consulta_original = Cargo.objects.all()
    filtro = CargoFilter(
        data={"nome": "Eletric"},
        queryset=consulta_original,
    )

    assert filtro.is_valid()
    assert filtro.form.cleaned_data["nome"] == "Eletric"

    consulta_sql, parametros = filtro.qs.query.sql_with_params()

    assert "nome" in consulta_sql
    assert any("Eletric" in str(parametro) for parametro in parametros)
    assert len(filtro.qs.query.where.children) == (
        len(consulta_original.query.where.children) + 1
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("true", True),
        ("false", False),
    ],
)
def test_filtrar_cargos_por_exigencia_de_documento(
    valor: str,
    esperado: bool,
) -> None:
    """Converte o valor da URL e aplica o filtro booleano."""
    consulta_original = Cargo.objects.all()
    filtro = CargoFilter(
        data={"exige_documento": valor},
        queryset=consulta_original,
    )

    assert filtro.is_valid()
    assert filtro.form.cleaned_data["exige_documento"] is esperado
    assert len(filtro.qs.query.where.children) == (
        len(consulta_original.query.where.children) + 1
    )


@pytest.mark.django_db
def test_permitir_consulta_sem_filtros() -> None:
    """Mantém a consulta original quando não há filtros."""
    consulta_original = Cargo.objects.all()
    filtro = CargoFilter(
        data={},
        queryset=consulta_original,
    )

    assert filtro.is_valid()
    assert str(filtro.qs.query) == str(consulta_original.query)
