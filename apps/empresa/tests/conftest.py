"""Fixtures compartilhadas para os testes do app Empresa."""

import pytest
from rest_framework.test import APIClient

from apps.empresa.models import Empresa
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def usuario_ativo(cargo_perfil_diretor):
    """Fixture de usuário autenticado utilizado nos testes de Empresa."""
    return Usuario.objects.create(
        username="9876543219",
        nome="João da Silva",
        registro_funcional=None,
        cpf="9876543219",
        email="joao@email.com",
        cargo=cargo_perfil_diretor,
        is_active=True,
    )


@pytest.fixture
def api_client(usuario_ativo):
    """Fornece um cliente HTTP do DRF autenticado com um usuário ativo."""
    client = APIClient()
    client.force_authenticate(user=usuario_ativo)
    return client


@pytest.fixture
def empresa_payload_valido():
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
def empresa(empresa_payload_valido, db):
    """Fixture de empresa persistida utilizada nos testes de Responsável."""
    return Empresa.objects.create(**empresa_payload_valido)


@pytest.fixture
def responsavel_payload_valido(empresa):
    """Payload válido para criação de responsável técnico."""
    return {
        "empresa": empresa,
        "nome": "João Responsável",
        "tipo": "preposto",
        "email": "joao.responsavel@email.com",
    }
