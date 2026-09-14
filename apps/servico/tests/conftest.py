"""Fixtures compartilhadas para os testes do app Serviço."""

import pytest

from apps.servico.models import Servico


@pytest.fixture
def servico_payload_valido():
    """Payload válido para criação de serviço."""
    return {
        "nome": "Serviço de Jardinagem",
        "status": True,
    }


@pytest.fixture
def servico_cadastrado(db):
    """Cria e retorna um serviço já cadastrado."""
    return Servico.objects.create(
        nome="Serviço de Jardinagem",
        status=True,
    )
