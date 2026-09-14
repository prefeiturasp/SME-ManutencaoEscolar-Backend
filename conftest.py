"""Fixtures globais utilizadas pelos testes do projeto."""

import pytest
from rest_framework.test import APIClient, APIRequestFactory

from apps.empresa.models import Empresa
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def api_factory() -> APIRequestFactory:
    """Fixture que fornece uma instância do APIRequestFactory do DRF."""
    return APIRequestFactory()


@pytest.fixture
def api_cliente(usuario_ativo: Usuario) -> APIClient:
    """Retorna um cliente para requisições à API."""
    cliente = APIClient()
    cliente.force_authenticate(user=usuario_ativo)
    return cliente


@pytest.fixture
def usuario_ativo(cargo_perfil_diretor: CargoEOL) -> Usuario:
    """Fixture de usuario ativo."""
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
def usuario_inativo(cargo_perfil_diretor: CargoEOL) -> Usuario:
    """Fixture de usuario inativo."""
    return Usuario.objects.create(
        username="9876543211",
        nome="Pedro da Silva",
        registro_funcional=None,
        cpf="9876543211",
        email="joao@email.com",
        cargo=cargo_perfil_diretor,
        is_active=False,
    )


@pytest.fixture
def usuario_ativo_dict(usuario_ativo: Usuario) -> dict[str, object]:
    """Retorna os dados esperados para a serialização do usuário ativo."""
    return {
        "id": usuario_ativo.id,
        "uuid": usuario_ativo.uuid,
        "nome": usuario_ativo.nome,
        "email": usuario_ativo.email,
        "registro_funcional": usuario_ativo.registro_funcional,
        "cpf": usuario_ativo.cpf,
        "username": usuario_ativo.username,
        "perfil_acesso": {
            "cargo": usuario_ativo.cargo.nome,
            "perfil": {
                "codigo": usuario_ativo.perfil,
                "descricao": PerfilAcesso(usuario_ativo.perfil).label,
            },
        },
    }


@pytest.fixture
def cargo_perfil_diretor() -> CargoEOL:
    """Fixture do cargo de diretor de unidade escolar."""
    return CargoEOL.objects.create(
        codigo="9999",
        nome="Diretor",
        perfil=PerfilAcesso.UE,
    )


@pytest.fixture
def empresa_payload_valido() -> dict[str, str]:
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
def empresa(empresa_payload_valido: dict[str, str], db: None) -> Empresa:
    """Fixture de empresa persistida utilizada nos testes de Responsável."""
    return Empresa.objects.create(**empresa_payload_valido)
