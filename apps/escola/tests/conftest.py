import pytest
from rest_framework.test import APIClient

from apps.escola.models import TipoEscola
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def cargo_perfil_diretor():
    """Fixture do cargo de diretor de unidade escolar."""
    return CargoEOL.objects.create(
        codigo="9999",
        nome="Diretor",
        perfil=PerfilAcesso.UE,
    )


@pytest.fixture
def usuario_ativo(cargo_perfil_diretor):
    """Fixture de usuario ativo."""
    return Usuario.objects.create(
        username="9876543219",
        nome="João da Silva",
        registro_funcional=None,
        cpf="9876543219",
        cargo=cargo_perfil_diretor,
        is_active=True,
    )


@pytest.fixture
def cliente_api(usuario_ativo):
    """Retorna um cliente para requisições à API."""
    cliente = APIClient()
    cliente.force_authenticate(user=usuario_ativo)
    return cliente


@pytest.fixture
def tipos_escola():
    """Cria tipos de escola para utilização nos testes."""
    return TipoEscola.objects.bulk_create(
        [
            TipoEscola(
                codigo_eol=1,
                sigla="EMEF",
            ),
            TipoEscola(
                codigo_eol=2,
                sigla="EMEI",
            ),
            TipoEscola(
                codigo_eol=3,
                sigla="CEMEI",
            ),
        ]
    )
