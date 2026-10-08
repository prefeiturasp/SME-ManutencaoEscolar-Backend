"""Testes dos modelos do domínio Equipe."""

import pytest
from django.core.exceptions import ValidationError

from apps.empresa.models import Empresa
from apps.equipe.models import Equipe, ProfissionalEquipe
from apps.profissional.models import Profissional

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


def test_empresa_da_equipe_deve_pertencer_ao_lote(lote_centro):
    """Não permite empresa diferente da empresa do lote na equipe."""
    outra_empresa = Empresa.objects.create(nome="Outra empresa")
    equipe = Equipe(
        nome="Equipe Elétrica",
        empresa=outra_empresa,
        lote=lote_centro,
    )

    with pytest.raises(ValidationError) as exc_info:
        equipe.full_clean()

    assert exc_info.value.message_dict["empresa"] == [
        "A empresa informada não está associada ao lote selecionado."
    ]


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


def test_funcao_deve_pertencer_ao_profissional(
    empresa, lote_centro, funcao_profissional
):
    """Não permite vincular uma função pertencente a outro profissional."""
    equipe = Equipe.objects.create(
        nome="Equipe Elétrica",
        empresa=empresa,
        lote=lote_centro,
    )
    outro_profissional = Profissional.objects.create(
        nome="Outro Profissional",
        cpf="98765432101",
        rg="987654321",
    )
    vinculo = ProfissionalEquipe(
        equipe=equipe,
        profissional=outro_profissional,
        funcao=funcao_profissional,
    )

    with pytest.raises(ValidationError) as exc_info:
        vinculo.full_clean()

    assert exc_info.value.message_dict["funcao"] == [
        "A função informada não pertence ao profissional selecionado."
    ]
