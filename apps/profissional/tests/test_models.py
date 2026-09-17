"""Testes dos models do domínio Profissional."""

import pytest
from django.core.exceptions import ValidationError

from apps.profissional.models import (
    DocumentoFuncaoProfissional,
    FuncaoProfissional,
    Profissional,
)

pytestmark = pytest.mark.django_db


def test_representacoes_textuais(cargo_profissional):
    """Representa os models com seus dados relevantes."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )
    documento = DocumentoFuncaoProfissional.objects.create(
        nome="NR10", funcao_profissional=funcao
    )

    assert str(profissional) == "José - 12345678901"
    assert str(funcao) == "José - Eletricista"
    assert str(documento) == "NR10 - José - Eletricista"


def test_profissional_valida_cpf_e_rg_unicos():
    """Valida CPF e RG únicos entre registros ativos."""
    Profissional.objects.create(
        nome="Primeiro", cpf="12345678901", rg="123456789"
    )

    with pytest.raises(ValidationError):
        Profissional(
            nome="Segundo", cpf="12345678901", rg="987654321"
        ).full_clean()

    with pytest.raises(ValidationError):
        Profissional(
            nome="Terceiro", cpf="10987654321", rg="123456789"
        ).full_clean()


def test_funcao_valida_cargo_unico_por_profissional(cargo_profissional):
    """Impede cargo duplicado para o mesmo profissional ativo."""
    profissional = Profissional.objects.create(
        nome="José", cpf="12345678901", rg="123456789"
    )
    FuncaoProfissional.objects.create(
        profissional=profissional, cargo=cargo_profissional
    )

    with pytest.raises(ValidationError):
        FuncaoProfissional(
            profissional=profissional, cargo=cargo_profissional
        ).full_clean()
