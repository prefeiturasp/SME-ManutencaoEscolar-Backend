"""Testes dos serializers do app lote."""

from datetime import date
from types import SimpleNamespace
from typing import cast
from unittest.mock import patch

import pytest
from rest_framework import serializers

from apps.escola.models import DiretoriaRegional
from apps.escola.serializers.diretoria_regional_serializers import (
    DiretoriaRegionalSerializer,
)
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
        "Não é permitido informar a mesma diretoria regional mais de uma vez."
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

    mensagem = "O período final não pode ser anterior ao período inicial."

    assert str(exc_info.value.detail["periodo_final"]) == mensagem


def test_retorna_nome_curto_da_diretoria_regional() -> None:
    """Deve retornar o nome abreviado da Diretoria Regional."""
    diretoria_regional = DiretoriaRegional(
        pk=1,
        codigo="DRE-1",
        nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
        abreviacao="BT",
    )
    serializer = DiretoriaRegionalSerializer(
        instance=diretoria_regional,
    )

    resultado = serializer.data

    assert resultado["nome_curto"] == "DRE BUTANTA"


CODIGO_CONTRATO_VALIDO = "31/SME/2021-SME/COMPS"


def _dados_lote(empresa, **extra):
    return {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
        "codigo_contrato": CODIGO_CONTRATO_VALIDO,
        "empresa": str(empresa.uuid),
        "diretorias_regionais": [],
        "status": True,
        **extra,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "codigo",
    [CODIGO_CONTRATO_VALIDO, "ABC123", "12.345/2026-A", "  31/SME/2021  "],
)
def test_aceita_codigo_contrato_valido(empresa, codigo) -> None:
    """Deve aceitar letras, números e os separadores /, - e ."""
    serializer = LoteCriarSerializer(
        data=_dados_lote(empresa, codigo_contrato=codigo)
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["codigo_contrato"] == codigo.strip()


@pytest.mark.django_db
def test_exige_codigo_contrato(empresa) -> None:
    """O código do contrato é obrigatório no cadastro."""
    dados = _dados_lote(empresa)
    del dados["codigo_contrato"]

    serializer = LoteCriarSerializer(data=dados)

    assert not serializer.is_valid()
    assert "codigo_contrato" in serializer.errors


@pytest.mark.django_db
@pytest.mark.parametrize("codigo", ["", "   ", None])
def test_rejeita_codigo_contrato_vazio(empresa, codigo) -> None:
    """Não aceita valor vazio, só espaços ou nulo."""
    serializer = LoteCriarSerializer(
        data=_dados_lote(empresa, codigo_contrato=codigo)
    )

    assert not serializer.is_valid()
    assert "codigo_contrato" in serializer.errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "codigo", ["31 SME", "31_SME", "31/SME#1", "contrato ação", "<b>1</b>"]
)
def test_rejeita_codigo_contrato_com_caracteres_invalidos(
    empresa, codigo
) -> None:
    """Rejeita espaços internos e caracteres fora do padrão permitido."""
    serializer = LoteCriarSerializer(
        data=_dados_lote(empresa, codigo_contrato=codigo)
    )

    assert not serializer.is_valid()
    assert "Código do contrato inválido" in str(
        serializer.errors["codigo_contrato"][0]
    )


@pytest.mark.django_db
def test_rejeita_codigo_contrato_acima_de_100_caracteres(empresa) -> None:
    """Respeita o tamanho máximo do campo."""
    serializer = LoteCriarSerializer(
        data=_dados_lote(empresa, codigo_contrato="A" * 101)
    )

    assert not serializer.is_valid()
    assert "codigo_contrato" in serializer.errors


def test_expoe_codigo_contrato_na_resposta() -> None:
    """Deve incluir o código do contrato na serialização do lote."""
    assert "codigo_contrato" in LoteSerializer.Meta.fields
    assert "codigo_contrato" in LoteCriarSerializer.Meta.fields
