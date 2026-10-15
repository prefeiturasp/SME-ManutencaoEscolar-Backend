"""Testes dos filtros do domínio Equipe."""

import pytest

from apps.empresa.models import Empresa
from apps.equipe.filters import EquipeFilter
from apps.equipe.models import Equipe
from apps.lote.models import Lote

pytestmark = pytest.mark.django_db


def test_filtra_equipes_pelo_nome(
    equipe_existente_ativa: Equipe,
    empresa: Empresa,
    lote_centro: Lote,
) -> None:
    """Filtra equipes pelo nome parcial."""
    Equipe.objects.create(
        nome="Equipe Hidráulica",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )

    resultado = EquipeFilter(
        {"nome": "Exist"},
        queryset=Equipe.objects.all(),
    ).qs

    assert list(resultado) == [equipe_existente_ativa]


def test_filtra_equipes_pelo_nome_da_empresa(
    equipe_existente_ativa: Equipe,
    empresa: Empresa,
) -> None:
    """Filtra equipes pelo nome parcial da empresa relacionada."""
    resultado = EquipeFilter(
        {"empresa": empresa.uuid},
        queryset=Equipe.objects.all(),
    ).qs

    assert list(resultado) == [equipe_existente_ativa]


def test_filtra_equipes_pela_situacao(
    equipe_existente_ativa: Equipe,
    empresa: Empresa,
    lote_centro: Lote,
) -> None:
    """Filtra equipes pela situação ativa ou inativa."""
    Equipe.objects.create(
        nome="Equipe inativa",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )

    resultado = EquipeFilter(
        {"situacao": "true"},
        queryset=Equipe.objects.all(),
    ).qs

    assert list(resultado) == [equipe_existente_ativa]


def test_filtra_equipes_pelo_nome_do_lote(
    equipe_existente_ativa: Equipe,
    lote_centro: Lote,
) -> None:
    """Filtra equipes pelo nome parcial do lote relacionado."""
    resultado = EquipeFilter(
        {"lote": lote_centro.uuid},
        queryset=Equipe.objects.all(),
    ).qs

    assert list(resultado) == [equipe_existente_ativa]
