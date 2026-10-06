"""Testes dos modelos do domínio Equipe."""

import pytest
from django.core.exceptions import ValidationError

from apps.equipe.models import Equipe, ProfissionalEquipe

pytestmark = pytest.mark.django_db


def test_representacao_textual_da_equipe(empresa, lote_centro):
    """Representa a equipe pelo nome."""
    equipe = Equipe.objects.create(
        nome="Equipe Elétrica",
        empresa=empresa,
        lote=lote_centro,
    )

    assert str(equipe) == "Equipe Elétrica"


def test_representacao_textual_do_profissional_na_equipe(
    empresa, lote_centro, profissional_ativo, funcao_profissional
):
    """Representa o vínculo pelo profissional e pela equipe."""
    equipe = Equipe.objects.create(
        nome="Equipe Elétrica",
        empresa=empresa,
        lote=lote_centro,
    )
    vinculo = ProfissionalEquipe.objects.create(
        equipe=equipe,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    assert str(vinculo) == f"{profissional_ativo} - {equipe}"


def test_nome_da_equipe_deve_ser_unico_na_empresa(empresa, lote_centro):
    """Não permite nomes repetidos, sem diferenciar maiúsculas, na empresa."""
    Equipe.objects.create(
        nome="Equipe Elétrica",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    repetida = Equipe(
        nome="equipe elétrica",
        situacao=False,
        empresa=empresa,
        lote=lote_centro,
    )

    with pytest.raises(ValidationError):
        repetida.full_clean()


def test_profissional_nao_pode_repetir_na_mesma_equipe(
    empresa, lote_centro, profissional_ativo, funcao_profissional
):
    """Protege no modelo a unicidade do profissional dentro da equipe."""
    equipe = Equipe.objects.create(
        nome="Equipe Elétrica",
        situacao=True,
        empresa=empresa,
        lote=lote_centro,
    )
    ProfissionalEquipe.objects.create(
        equipe=equipe,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )
    repetido = ProfissionalEquipe(
        equipe=equipe,
        profissional=profissional_ativo,
        funcao=funcao_profissional,
    )

    with pytest.raises(ValidationError):
        repetido.full_clean()
