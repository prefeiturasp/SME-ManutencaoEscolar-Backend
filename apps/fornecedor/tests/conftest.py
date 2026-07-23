"""Fixtures compartilhadas para os testes do app Fornecedor."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fornece um cliente HTTP do DRF."""
    return APIClient()


@pytest.fixture
def fornecedor_payload_valido():
    """Payload válido para criação de fornecedor."""
    return {
        "nome": "Fornecedor Exemplo",
        "cnpj": "12345678901234",
        "razao_social": "Fornecedor Exemplo LTDA",
        "link_rastreio": "https://www.exemplo.com/rastreio",
        "cep": "12345678",
        "logradouro": "Rua Exemplo",
        "numero": "123",
        "complemento": "Apto 101",
        "cidade": "São Paulo",
        "estado": "SP",
    }
