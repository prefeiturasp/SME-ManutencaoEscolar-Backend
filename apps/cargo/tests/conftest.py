"""Fixtures compartilhadas para os testes do app Cargo."""

import pytest

from django.utils import timezone

from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.services.cargo_service import CargoService


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


@pytest.fixture
def service():
    """Serviço de cargos configurado para os testes."""
    return CargoService()


@pytest.fixture
def documentos_cargo_payload_valido() -> list[dict[str, str]]:
    """Lista válida de documentos de cargo."""
    return [
        {
            "nome": "Certificado NR-10",
        },
        {
            "nome": "Certificado NR-35",
        },
    ]


@pytest.fixture
def cargo_payload_valido(
    documentos_cargo_payload_valido: list[dict[str, str]],
) -> dict[str, object]:
    """Payload válido para criação de cargo com documentos."""
    return {
        "nome": "Engenheiro Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": documentos_cargo_payload_valido,
    }


@pytest.fixture
def cargo_payload_valido_sem_documentos() -> dict[str, object]:
    """Payload válido para criação de cargo sem documentos."""
    return {
        "nome": "Auxiliar Administrativo",
        "exige_documento": False,
        "status": True,
        "documentos": [],
    }
