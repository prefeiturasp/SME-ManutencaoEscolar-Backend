"""Fixtures dos testes do domínio Equipe."""

import pytest

from apps.cargo.models import Cargo
from apps.profissional.models import FuncaoProfissional, Profissional


@pytest.fixture
def profissional_ativo(db: None) -> Profissional:
    """Cria um profissional ativo."""
    return Profissional.objects.create(
        nome="João Eletricista",
        cpf="12345678901",
        rg="123456789",
        status=True,
    )


@pytest.fixture
def funcao_profissional(
    profissional_ativo: Profissional,
) -> FuncaoProfissional:
    """Cria uma função para o profissional ativo."""
    cargo = Cargo.objects.create(nome="Eletricista")
    return FuncaoProfissional.objects.create(
        profissional=profissional_ativo,
        cargo=cargo,
    )


@pytest.fixture
def equipe_payload(
    empresa,
    lote_centro,
    profissional_ativo: Profissional,
    funcao_profissional: FuncaoProfissional,
) -> dict[str, object]:
    """Retorna um payload válido para criação de equipe."""
    return {
        "nome": "Equipe Elétrica",
        "situacao": True,
        "empresa": str(empresa.uuid),
        "lote": str(lote_centro.uuid),
        "profissionais": [
            {
                "profissional": str(profissional_ativo.uuid),
                "funcao": str(funcao_profissional.uuid),
            }
        ],
    }
