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


def test_obtem_nome_da_diretoria_regional_do_usuario(
    cargo_dre: CargoEOL, diretoria_regional_centro: DiretoriaRegional
) -> None:
    """Retorna o nome da DRE vinculada ao usuário."""
    _criar_usuario(
        "1000001",
        cargo=cargo_dre,
        diretoria_regional=diretoria_regional_centro,
    )

    nome = UsuarioRepository.obter_nome_diretoria_regional("1000001")

    assert nome == diretoria_regional_centro.nome


@pytest.mark.parametrize("username", ["1000002", "inexistente"])
def test_nome_da_diretoria_regional_e_nulo_sem_vinculo(
    cargo_dre: CargoEOL, username: str
) -> None:
    """Retorna nulo para usuário sem vínculo ou inexistente."""
    _criar_usuario("1000002", cargo=cargo_dre)

    assert UsuarioRepository.obter_nome_diretoria_regional(username) is None


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

    assert resultado["diretoria_regional"] == diretoria_regional_centro.nome


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


def _dados_eol(dre: object) -> dict[str, object]:
    return {
        "nome": "Ana Gestora",
        "email": "ana@dre.com",
        "codigo_rf": "1234567",
        "cpf": "12345678900",
        "dre": dre,
    }


@pytest.mark.parametrize(
    "valor",
    [
        "DRE-CENTRO",
        "dre centro",
        " Dre Centro ",
        "dc",
        "DC",
    ],
)
def test_login_vincula_a_dre_informada_pelo_eol(
    diretoria_regional_centro: DiretoriaRegional, valor: str
) -> None:
    """Associa o usuário à DRE pelo código, nome ou abreviação."""
    diretoria_regional_centro.codigo = "DRE-CENTRO"
    diretoria_regional_centro.nome = "DRE Centro"
    diretoria_regional_centro.abreviacao = "DC"
    diretoria_regional_centro.save()

    UsuarioRepository.atualizar_ou_criar(_dados_eol(valor))

    usuario = Usuario.objects.get(registro_funcional="1234567")
    assert usuario.diretoria_regional == diretoria_regional_centro


@pytest.mark.parametrize("valor", [None, "", "  ", "DRE INEXISTENTE"])
def test_login_sem_dre_valida_nao_vincula(valor: object) -> None:
    """Deixa o usuário sem DRE quando o EOL não informa uma DRE válida."""
    UsuarioRepository.atualizar_ou_criar(_dados_eol(valor))

    usuario = Usuario.objects.get(registro_funcional="1234567")
    assert usuario.diretoria_regional is None


def test_login_ignora_dre_quando_chave_ausente() -> None:
    """Aceita respostas do EOL sem o campo da DRE."""
    dados = _dados_eol(None)
    del dados["dre"]

    UsuarioRepository.atualizar_ou_criar(dados)

    usuario = Usuario.objects.get(registro_funcional="1234567")
    assert usuario.diretoria_regional is None


def test_login_atualiza_a_dre_de_usuario_existente(
    diretoria_regional_centro: DiretoriaRegional,
) -> None:
    """Mantém o vínculo da DRE sincronizado a cada login."""
    UsuarioRepository.atualizar_ou_criar(_dados_eol(None))

    UsuarioRepository.atualizar_ou_criar(
        _dados_eol(diretoria_regional_centro.codigo)
    )
    usuario = Usuario.objects.get(registro_funcional="1234567")
    assert usuario.diretoria_regional == diretoria_regional_centro

    UsuarioRepository.atualizar_ou_criar(_dados_eol(None))
    usuario.refresh_from_db()
    assert usuario.diretoria_regional is None
