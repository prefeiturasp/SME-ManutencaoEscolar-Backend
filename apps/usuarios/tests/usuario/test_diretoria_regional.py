"""Testes do vínculo entre usuários DRE e diretorias regionais."""

import pytest

from apps.escola.models import DiretoriaRegional
from apps.usuarios.constants import PerfilAcesso
from apps.usuarios.models import CargoEOL, Usuario
from apps.usuarios.repository.usuario_repository import UsuarioRepository
from apps.usuarios.services.usuario_service import UsuarioService

pytestmark = pytest.mark.django_db


@pytest.fixture
def cargo_dre() -> CargoEOL:
    """Cria um cargo com perfil DRE."""
    return CargoEOL.objects.create(
        codigo="7001", nome="Gestor DRE", perfil=PerfilAcesso.DRE
    )


@pytest.fixture
def outra_dre() -> DiretoriaRegional:
    """Cria uma segunda diretoria regional."""
    return DiretoriaRegional.objects.create(
        codigo="DRE-OUTRA", nome="DRE OUTRA", abreviacao="DO"
    )


def _criar_usuario(username: str, **campos: object) -> Usuario:
    dados: dict[str, object] = {
        "username": username,
        "nome": f"Usuário {username}",
        "email": f"{username}@teste.com",
    }
    dados.update(campos)
    return Usuario.objects.create(**dados)


def test_me_retorna_a_dre_do_usuario_dre(
    cargo_dre: CargoEOL, diretoria_regional_centro: DiretoriaRegional
) -> None:
    """Usa o vínculo do usuário para informar a DRE no /me."""
    _criar_usuario(
        "1000003",
        cargo=cargo_dre,
        diretoria_regional=diretoria_regional_centro,
    )

    resultado = UsuarioService.obter_usuario_autenticado("1000003")

    assert resultado["diretoria_regional"] == {
        "id": diretoria_regional_centro.id,
        "codigo": diretoria_regional_centro.codigo,
        "nome": diretoria_regional_centro.nome,
        "abreviacao": diretoria_regional_centro.abreviacao,
        "nome_curto": diretoria_regional_centro.nome_curto,
    }


def test_obter_diretoria_regional_retorna_nulo_sem_vinculo() -> None:
    """Retorna ``None`` quando o usuário não tem DRE vinculada."""
    _criar_usuario("1000004", diretoria_regional=None)

    assert UsuarioRepository.obter_diretoria_regional("1000004") is None


def test_obter_diretoria_regional_retorna_nulo_sem_usuario() -> None:
    """Retorna ``None`` quando não encontra o usuário informado."""
    assert UsuarioRepository.obter_diretoria_regional("inexistente") is None


def test_lista_apenas_gestores_dre_elegiveis(
    cargo_dre: CargoEOL,
    cargo_perfil_diretor: CargoEOL,
    diretoria_regional_centro: DiretoriaRegional,
    outra_dre: DiretoriaRegional,
) -> None:
    """Lista usuários DRE ativos, com e-mail, da diretoria regional."""
    centro = {"diretoria_regional": diretoria_regional_centro}
    _criar_usuario(
        "1000010", cargo=cargo_dre, registro_funcional="1000010", **centro
    )
    _criar_usuario("1000011", cargo=cargo_dre, is_active=False, **centro)
    _criar_usuario("1000012", cargo=cargo_dre, email="", **centro)
    _criar_usuario("1000013", cargo=cargo_dre, email="  ", **centro)
    _criar_usuario("1000014", cargo=cargo_dre, diretoria_regional=outra_dre)
    _criar_usuario("1000015", cargo=cargo_perfil_diretor, **centro)
    _criar_usuario("1000016", cargo=None, **centro)

    gestores = UsuarioRepository.listar_gestores_dre(
        diretoria_regional_centro.id
    )

    assert gestores == [
        {
            "nome": "Usuário 1000010",
            "email": "1000010@teste.com",
            "registro_funcional": "1000010",
        }
    ]
