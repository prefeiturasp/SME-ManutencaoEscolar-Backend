"""Fixtures compartilhadas para os testes do app Cargo."""

import pytest

from django.utils import timezone

from apps.cargo.models import Cargo, DocumentoCargo


@pytest.fixture
def cargo(db):
    """Cargo ativo persistido para os testes."""
    return Cargo.objects.create(
        nome="Eletricista",
        exige_documento=False,
        status=True,
    )


@pytest.fixture
def cargo_deletado(db, usuario_ativo):
    """Cargo deletado logicamente para os testes."""
    return Cargo.objects.create(
        nome="Cargo deletado",
        exige_documento=False,
        status=False,
        deletado_em=timezone.now(),
        deletado_por=usuario_ativo,
    )


@pytest.fixture
def documento_cargo(db, cargo, usuario_ativo):
    """Documento vinculado a um cargo para os testes."""
    return DocumentoCargo.objects.create(
        nome="Certificado NR-10",
        cargo=cargo,
        criado_por=usuario_ativo,
        atualizado_por=usuario_ativo,
    )


@pytest.fixture
def documento_cargo_payload_valido():
    """Payload válido de documento de cargo."""
    return {
        "nome": "Certificado NR-10",
    }


@pytest.fixture
def cargo_payload_atualizacao_valido():
    """Payload válido para atualização parcial de cargo."""
    return {
        "nome": "Eletricista atualizado",
        "exige_documento": True,
        "status": False,
        "documentos": [
            {
                "nome": "Certificado NR-10 atualizado",
            },
        ],
    }
