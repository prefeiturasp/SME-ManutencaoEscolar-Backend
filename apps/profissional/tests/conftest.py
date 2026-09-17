"""Fixtures dos testes do domínio Profissional."""

import pytest

from apps.cargo.models import Cargo


@pytest.fixture
def cargo_profissional(db: None) -> Cargo:
    """Cria um cargo disponível para vincular ao profissional."""
    return Cargo.objects.create(nome="Eletricista", exige_documento=True)


@pytest.fixture
def profissional_payload(cargo_profissional: Cargo) -> dict[str, object]:
    """Retorna um payload válido de profissional."""
    return {
        "nome": "José da Silva",
        "cpf": "12345678901",
        "rg": "123456789",
        "status": True,
        "funcoes": [
            {
                "uuid_cargo": str(cargo_profissional.uuid),
                "documentos": [{"nome": "Certificado NR10"}],
            }
        ],
    }
