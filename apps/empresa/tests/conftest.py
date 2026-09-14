"""Fixtures compartilhadas para os testes do app Empresa."""

import pytest


@pytest.fixture
def responsavel_payload_valido(empresa):
    """Payload válido para criação de responsável técnico."""
    return {
        "empresa": empresa,
        "nome": "João Responsável",
        "tipo": "preposto",
        "email": "joao.responsavel@email.com",
        "telefone": "11987654321",
    }


@pytest.fixture
def responsavel_tecnico_payload_valido():
    """Payload válido para um responsável aninhado no serializer de empresa."""
    return {
        "tipo": "preposto",
        "nome": "João Responsável",
        "email": "joao.responsavel@email.com",
        "telefone": "11987654321",
    }


@pytest.fixture
def empresa_payload_valido_com_responsaveis(
    empresa_payload_valido, responsavel_tecnico_payload_valido
):
    """Payload válido de empresa com responsáveis técnicos aninhados."""
    return {
        **empresa_payload_valido,
        "responsaveis_tecnicos": [responsavel_tecnico_payload_valido],
    }
