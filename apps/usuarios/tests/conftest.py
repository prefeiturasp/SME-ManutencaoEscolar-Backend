import pytest

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
        email="joao@email.com",
        cargo=cargo_perfil_diretor,
        is_active=True,
    )


@pytest.fixture
def usuario_inativo(cargo_perfil_diretor):
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
def usuario_ativo_dict(usuario_ativo):
    """Fixture de usuario inativo retornando em diconario."""
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
