"""Testes dos filtros do domínio Serviço."""

import pytest

from apps.servico.filters import ServicoFilter, _converter_status
from apps.servico.models import Servico


@pytest.fixture
def servicos(db):
    """Cria serviços para os testes dos filtros."""
    servico_ativo = Servico.objects.create(
        nome="Pintura",
        status=True,
    )
    servico_inativo = Servico.objects.create(
        nome="Manutenção elétrica",
        status=False,
    )
    outro_servico_ativo = Servico.objects.create(
        nome="Manutenção hidráulica",
        status=True,
    )

    return {
        "ativo": servico_ativo,
        "inativo": servico_inativo,
        "outro_ativo": outro_servico_ativo,
    }


@pytest.mark.parametrize(
    ("valor", "resultado_esperado"),
    [
        ("true", True),
        ("false", False),
        ("qualquer-valor", False),
        ("", False),
    ],
)
def test_deve_converter_status(
    valor: str,
    resultado_esperado: bool,
):
    """Deve converter somente a string true para verdadeiro."""
    assert _converter_status(valor) is resultado_esperado


def test_deve_filtrar_servicos_pelo_nome(servicos):
    """Deve filtrar serviços utilizando parte do nome."""
    queryset = Servico.objects.all()

    filtro = ServicoFilter(
        data={"nome": "Manutenção"},
        queryset=queryset,
    )

    assert filtro.is_valid()
    assert filtro.filters["nome"].lookup_expr == "icontains"

    nomes = set(
        filtro.qs.values_list(
            "nome",
            flat=True,
        )
    )

    assert nomes == {
        "Manutenção elétrica",
        "Manutenção hidráulica",
    }


def test_deve_filtrar_servicos_ativos(servicos):
    """Deve retornar somente os serviços ativos."""
    queryset = Servico.objects.all()

    filtro = ServicoFilter(
        data={"status": "true"},
        queryset=queryset,
    )

    assert filtro.is_valid()

    nomes = set(
        filtro.qs.values_list(
            "nome",
            flat=True,
        )
    )

    assert nomes == {
        "Pintura",
        "Manutenção hidráulica",
    }


def test_deve_filtrar_servicos_inativos(servicos):
    """Deve retornar somente os serviços inativos."""
    queryset = Servico.objects.all()

    filtro = ServicoFilter(
        data={"status": "false"},
        queryset=queryset,
    )

    assert filtro.is_valid()

    nomes = list(
        filtro.qs.values_list(
            "nome",
            flat=True,
        )
    )

    assert nomes == ["Manutenção elétrica"]


def test_deve_combinar_nome_e_status(servicos):
    """Deve aplicar os filtros de nome e status em conjunto."""
    queryset = Servico.objects.all()

    filtro = ServicoFilter(
        data={
            "nome": "manutenção",
            "status": "true",
        },
        queryset=queryset,
    )

    assert filtro.is_valid()

    nomes = list(
        filtro.qs.values_list(
            "nome",
            flat=True,
        )
    )

    assert nomes == ["Manutenção hidráulica"]


def test_deve_rejeitar_status_invalido(servicos):
    """Deve considerar inválido um status fora das opções."""
    queryset = Servico.objects.all()

    filtro = ServicoFilter(
        data={"status": "invalido"},
        queryset=queryset,
    )

    assert not filtro.is_valid()
    assert "status" in filtro.errors
