"""Testes dos serializers do app lote."""

from datetime import date
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

import pytest
from rest_framework import serializers

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote
from apps.lote.serializers import (
    LoteCriarSerializer,
    LoteSerializer,
)


def criar_diretoria_regional(pk: int) -> DiretoriaRegional:
    """Cria uma DRE não persistida para os testes."""
    return DiretoriaRegional(pk=pk)


def test_retorna_diretorias_regionais_serializadas() -> None:
    """Deve retornar os dados serializados das DREs do lote."""
    diretorias_regionais = [
        criar_diretoria_regional(1),
        criar_diretoria_regional(2),
    ]
    lote = cast(
        Lote,
        SimpleNamespace(
            diretorias_regionais=diretorias_regionais,
        ),
    )
    resultado_esperado = [
        {
            "id": 1,
            "codigo": "DRE-1",
            "nome": "Diretoria Regional 1",
            "abreviacao": "DR1",
        },
        {
            "id": 2,
            "codigo": "DRE-2",
            "nome": "Diretoria Regional 2",
            "abreviacao": "DR2",
        },
    ]

    with patch(
        "apps.lote.serializers.DiretoriaRegionalSerializer",
    ) as serializer_mock:
        serializer_mock.return_value.data = resultado_esperado

        resultado = LoteSerializer().get_diretorias_regionais(lote)

    assert resultado == resultado_esperado
    serializer_mock.assert_called_once_with(
        diretorias_regionais,
        many=True,
    )


def test_aceita_diretorias_regionais_diferentes() -> None:
    """Deve aceitar DREs sem identificadores repetidos."""
    diretorias_regionais = [
        criar_diretoria_regional(1),
        criar_diretoria_regional(2),
    ]
    serializer = LoteCriarSerializer()

    resultado = serializer.validate_diretorias_regionais(
        diretorias_regionais,
    )

    assert resultado == diretorias_regionais


def test_rejeita_diretorias_regionais_repetidas() -> None:
    """Deve rejeitar DREs com identificadores repetidos."""
    diretorias_regionais = [
        criar_diretoria_regional(1),
        criar_diretoria_regional(1),
    ]
    serializer = LoteCriarSerializer()

    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_diretorias_regionais(
            diretorias_regionais,
        )

    mensagem = (
        "Não é permitido informar a mesma diretoria regional "
        "mais de uma vez."
    )
    assert str(exc_info.value.detail[0]) == mensagem


@pytest.mark.parametrize(
    ("periodo_inicial", "periodo_final"),
    [
        (None, None),
        (date(2026, 1, 1), None),
        (None, date(2026, 12, 31)),
        (date(2026, 1, 1), date(2026, 1, 1)),
        (date(2026, 1, 1), date(2026, 12, 31)),
    ],
)
def test_aceita_periodos_validos(
    periodo_inicial: date | None,
    periodo_final: date | None,
) -> None:
    """Deve aceitar períodos válidos ou incompletos."""
    attrs = {
        "periodo_inicial": periodo_inicial,
        "periodo_final": periodo_final,
    }
    serializer = LoteCriarSerializer()

    resultado = serializer.validate(attrs)

    assert resultado == attrs


def test_rejeita_periodo_final_anterior_ao_inicial() -> None:
    """Deve rejeitar período final anterior ao inicial."""
    attrs = {
        "periodo_inicial": date(2026, 12, 31),
        "periodo_final": date(2026, 1, 1),
    }
    serializer = LoteCriarSerializer()

    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate(attrs)

    mensagem = (
        "O período final não pode ser anterior "
        "ao período inicial."
    )
    assert str(exc_info.value.detail["periodo_final"]) == mensagem
