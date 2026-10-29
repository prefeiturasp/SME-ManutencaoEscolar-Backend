"""Fixtures globais utilizadas pelos testes do projeto."""

from collections.abc import Callable
from typing import Any

import pytest
from rest_framework.test import APIClient, APIRequestFactory

from apps.empresa.models import Empresa
from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.models.responsavel_unidade import (
    HistoricoResponsavel,
    ResponsavelUnidade,
)
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.tipos_escola import TipoEscola
from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.lote.models import Lote, LoteDiretoriaRegional
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
def api_cliente_perfil(db: Any) -> Callable[[str | None], APIClient]:
    """Retorna uma fábrica de clientes autenticados com o perfil informado.

    Com ``None`` cria um usuário sem cargo vinculado.
    """

    def _criar(perfil: str | None) -> APIClient:
        cargo = None
        if perfil is not None:
            cargo = CargoEOL.objects.create(
                codigo=f"perfil-{perfil}",
                nome=f"Cargo {perfil}",
                perfil=perfil,
            )
        usuario = Usuario.objects.create(
            username=f"usuario-{perfil}",
            nome=f"Usuário {perfil}",
            cargo=cargo,
            is_active=True,
        )
        cliente = APIClient()
        cliente.force_authenticate(user=usuario)
        return cliente

    return _criar


@pytest.fixture
def cargo_perfil_diretor() -> CargoEOL:
    """Fixture do cargo de diretor de unidade escolar."""
    return CargoEOL.objects.create(
        codigo="9999",
        nome="Diretor",
        perfil=PerfilAcesso.UE,
    )


@pytest.fixture
def cargo_perfil_sme() -> CargoEOL:
    """Fixture de um cargo com perfil GME/SME."""
    return CargoEOL.objects.create(
        codigo="8888",
        nome="Gestor SME",
        perfil=PerfilAcesso.SME,
    )


@pytest.fixture
def usuario_ativo(cargo_perfil_sme: CargoEOL) -> Usuario:
    """Fixture de usuario ativo, com perfil GME/SME."""
    return Usuario.objects.create(
        username="9876543219",
        nome="João da Silva",
        registro_funcional=None,
        cpf="9876543219",
        email="joao@email.com",
        cargo=cargo_perfil_sme,
        is_active=True,
    )


@pytest.fixture
def usuario_ue(cargo_perfil_diretor: CargoEOL) -> Usuario:
    """Fixture de usuario ativo com perfil de Unidade Educacional (UE)."""
    return Usuario.objects.create(
        username="11122233344",
        nome="Maria Diretora",
        registro_funcional=None,
        cpf="11122233344",
        email="maria@email.com",
        cargo=cargo_perfil_diretor,
        is_active=True,
    )


@pytest.fixture
def api_cliente_ue(usuario_ue: Usuario) -> APIClient:
    """Retorna um cliente para requisições à API autenticado como UE."""
    cliente = APIClient()
    cliente.force_authenticate(user=usuario_ue)
    return cliente


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
    assert usuario_ativo.cargo is not None
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
                "descricao": (
                    PerfilAcesso(usuario_ativo.perfil).label
                    if usuario_ativo.perfil is not None
                    else None
                ),
            },
        },
        "funcionalidades": usuario_ativo.funcionalidades,
    }


@pytest.fixture
def usuario_sincronizacao(cargo_perfil_sme: CargoEOL) -> Usuario:
    """Configura o usuário global como responsável pela sincronização."""
    return Usuario.objects.create(
        username="sincronizacao_eol",
        nome="Sincronizador Dados do EOL",
        registro_funcional=None,
        cpf=None,
        cargo=cargo_perfil_sme,
        is_active=False,
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


@pytest.fixture
def configurar_api_eol(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configura as variáveis da API EOL para os testes."""
    comandos = []
    comandos_app_escola = [
        "sincronizar_tipos_escolas",
        "sincronizar_subprefeituras",
        "sincronizar_escolas",
        "sincronizar_diretores",
        "sincronizar_dados_escolas",
    ]
    for comando in comandos_app_escola:
        comandos.append(f"apps.escola.management.commands.{comando}")

    comandos_app_usuario = ["sincronizar_cargos_eol"]
    for comando in comandos_app_usuario:
        comandos.append(f"apps.usuarios.management.commands.{comando}")

    for modulo in comandos:
        monkeypatch.setattr(
            f"{modulo}.SME_API_EOL_URL",
            "https://api-eol-teste",
        )
        monkeypatch.setattr(
            f"{modulo}.SME_API_EOL_TOKEN",
            "token-teste",
        )


@pytest.fixture
def diretoria_regional_centro() -> DiretoriaRegional:
    """Cria uma Diretoria Regional para os testes."""
    return DiretoriaRegional.objects.create(
        codigo="DRE01",
        nome="DIRETORIA REGIONAL DE EDUCACAO CENTRO",
        abreviacao="CT",
    )


@pytest.fixture
def lote_centro(
    diretoria_regional_centro: DiretoriaRegional, empresa: Empresa
) -> Lote:
    """Fixture de lote."""
    lote = Lote.objects.create(
        codigo_cadastro="LOTE-001",
        nome="Lote Centro",
        empresa=empresa,
        status=True,
    )
    LoteDiretoriaRegional.objects.create(
        lote=lote,
        diretoria_regional=diretoria_regional_centro,
    )
    return lote


@pytest.fixture
def tipo_escola_emef() -> TipoEscola:
    """Cria um tipo de escola EMEF."""
    return TipoEscola.objects.create(
        codigo_eol=1,
        sigla="EMEF",
    )


@pytest.fixture
def subprefeitura_se(
    diretoria_regional_centro: DiretoriaRegional,
) -> Subprefeitura:
    """Cria uma Subprefeitura para os testes."""
    subprefeitura = Subprefeitura.objects.create(
        codigo_eol="SP01",
        nome="Subprefeitura Sé",
    )
    subprefeitura.diretorias_regionais.add(diretoria_regional_centro)
    return subprefeitura


@pytest.fixture
def unidade_educacional_emef(
    diretoria_regional_centro: DiretoriaRegional,
    tipo_escola_emef: TipoEscola,
    subprefeitura_se: Subprefeitura,
    usuario_sincronizacao: Usuario,
) -> Unidadeeducacional:
    """Cria uma unidade educacional do tipo EMEF para testes."""
    return Unidadeeducacional.objects.create(
        codigo_eol="100001",
        nome="EMEF ESCOLA TESTE",
        diretoria_regional=diretoria_regional_centro,
        tipo_escola=tipo_escola_emef,
        subprefeitura=subprefeitura_se,
        status=True,
        atualizado_por=usuario_sincronizacao,
    )


@pytest.fixture
def responsavel_unidade() -> ResponsavelUnidade:
    """Cria um responsável de unidade para os testes."""
    return ResponsavelUnidade.objects.create(
        registro_funcional="0000011",
        nome="DIRETOR TESTE",
        email="responsavel.emef@teste.com",
        telefone="11999999999",
        esta_afastado=False,
    )


@pytest.fixture
def historico_responsavel(
    responsavel_unidade: ResponsavelUnidade,
    unidade_educacional_emef: Unidadeeducacional,
    cargo_perfil_diretor: CargoEOL,
) -> HistoricoResponsavel:
    """Cria um histórico de responsável de unidade para os testes."""
    return HistoricoResponsavel.objects.create(
        responsavel=responsavel_unidade,
        unidade_educacional=unidade_educacional_emef,
        cargo=cargo_perfil_diretor,
        ativo=True,
    )
