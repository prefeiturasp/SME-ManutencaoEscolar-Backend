"""Fixtures globais utilizadas pelos testes do projeto."""

import pytest

from apps.empresa.models import Empresa
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL


@pytest.fixture
def cargo_perfil_diretor() -> CargoEOL:
    """Fixture do cargo de diretor de unidade escolar."""
    return CargoEOL.objects.create(
        codigo="9999",
        nome="Diretor",
        perfil=PerfilAcesso.UE,
    )


@pytest.fixture
def empresa_payload_valido() -> dict:
    """Payload válido para criação de empresa."""
    return {
        "nome": "Empresa Exemplo",
        "cnpj": "12345678901234",
        "razao_social": "Empresa Exemplo LTDA",
        "link_rastreio": "https://www.exemplo.com/rastreio",
        "cep": "12345678",
        "logradouro": "Rua Exemplo",
        "numero": "123",
        "complemento": "Apto 101",
        "cidade": "São Paulo",
        "estado": "SP",
    }


@pytest.fixture
def empresa(empresa_payload_valido: dict, db: None) -> Empresa:
    """Fixture de empresa persistida utilizada nos testes de Responsável."""
    return Empresa.objects.create(**empresa_payload_valido)
