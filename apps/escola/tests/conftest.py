from unittest.mock import Mock

import pytest
from rest_framework.test import APIClient

from apps.escola.models import TipoEscola
from apps.escola.models.diretoria_regional import DiretoriaRegional
from apps.escola.models.responsavel_unidade import ResponsavelUnidade
from apps.escola.models.subprefeitura import Subprefeitura
from apps.escola.models.unidade_educacional import Unidadeeducacional
from apps.lote.models import Lote, LoteDiretoriaRegional
from apps.usuarios.models.cargo_eol import CargoEOL
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def obter_cargo_diretor():
    """Retorna o cargo EOL de Diretor de Escola."""
    return CargoEOL.objects.get(
        nome="DIRETOR DE ESCOLA",
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
def tipo_escola_emef():
    """Cria um tipo de escola EMEF."""
    return TipoEscola.objects.create(
        codigo_eol=1,
        sigla="EMEF",
    )


@pytest.fixture
def tipo_escola_cemei():
    """Cria um tipo de escola CEMEI."""
    return TipoEscola.objects.create(
        codigo_eol=2,
        sigla="CEMEI",
    )


@pytest.fixture
def tipos_escola(tipo_escola_emef, tipo_escola_cemei):
    """Cria tipos de escola para utilização nos testes."""
    return [tipo_escola_emef, tipo_escola_cemei]


@pytest.fixture
def resposta_api_tipos_escolas():
    """Cria uma resposta simulada da API EOL."""
    resposta = Mock()
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "codigo": 1,
            "descricaoSigla": "EMEF",
        },
        {
            "codigo": 2,
            "descricaoSigla": "CEMEI",
        },
    ]
    return resposta


@pytest.fixture()
def configurar_api_eol(monkeypatch):
    """Configura as variáveis da API EOL para os testes."""
    comandos = (
        "sincronizar_tipos_escolas",
        "sincronizar_subprefeituras",
        "sincronizar_escolas",
        "sincronizar_diretores",
    )

    for comando in comandos:
        modulo = f"apps.escola.management.commands.{comando}"

        monkeypatch.setattr(
            f"{modulo}.SME_API_EOL_URL",
            "https://api-eol-teste",
        )
        monkeypatch.setattr(
            f"{modulo}.SME_API_EOL_TOKEN",
            "token-teste",
        )


@pytest.fixture
def diretoria_regional_centro():
    """Cria uma Diretoria Regional para os testes."""
    return DiretoriaRegional.objects.create(
        codigo="DRE01",
        nome="DIRETORIA REGIONAL DE EDUCACAO CENTRO",
        abreviacao="CT",
    )


@pytest.fixture
def diretoria_regional_ipiranga():
    """Cria uma Diretoria Regional para os testes."""
    return DiretoriaRegional.objects.create(
        codigo="DRE02",
        nome="DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
        abreviacao="IP",
    )


@pytest.fixture
def resposta_api_subprefeituras():
    """Retorna uma resposta simulada da API de Subprefeituras."""
    resposta = Mock()
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "codigoSubprefeitura": "SP01",
            "nomeSubprefeitura": "Subprefeitura Sé",
        },
        {
            "codigoSubprefeitura": "SP02",
            "nomeSubprefeitura": "Subprefeitura Lapa",
        },
    ]
    return resposta


@pytest.fixture
def subprefeitura_se(diretoria_regional_centro):
    """Cria uma Subprefeitura para os testes."""
    subprefeitura = Subprefeitura.objects.create(
        codigo_eol="SP01",
        nome="Subprefeitura Sé",
    )
    subprefeitura.diretorias_regionais.add(diretoria_regional_centro)
    return subprefeitura


@pytest.fixture
def subprefeitura_pirituba(diretoria_regional_ipiranga):
    """Cria uma Subprefeitura para os testes."""
    subprefeitura = Subprefeitura.objects.create(
        codigo_eol="SP02",
        nome="Subprefeitura Pirituba",
    )
    subprefeitura.diretorias_regionais.add(diretoria_regional_ipiranga)
    return subprefeitura


@pytest.fixture
def resposta_api_escolas():
    """Retorna uma resposta simulada da API de escolas."""
    resposta = Mock()
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "codigoEscola": "100001",
            "nomeEscola": "Escola Teste",
            "nomeDRE": "Diretoria Regional Centro",
            "siglaDRE": "DRE",
            "codigoDRE": "DRE01",
            "tipoEscola": "Escola Municipal",
            "siglaTipoEscola": "EMEF",
        },
    ]
    return resposta


@pytest.fixture
def respostas_api(
    resposta_api_escolas,
    resposta_api_subprefeituras,
):
    """Retorna as respostas simuladas das APIs."""
    return [
        resposta_api_escolas,
        resposta_api_subprefeituras,
    ]


@pytest.fixture
def unidade_educacional_emef(
    diretoria_regional_centro,
    tipo_escola_emef,
    subprefeitura_se,
):
    """Cria uma unidade educacional do tipo EMEF para testes."""
    return Unidadeeducacional.objects.create(
        codigo_eol="100001",
        nome="EMEF ESCOLA TESTE",
        diretoria_regional=diretoria_regional_centro,
        tipo_escola=tipo_escola_emef,
        subprefeitura=subprefeitura_se,
        status=True,
    )


@pytest.fixture
def unidade_educacional_inativa_emef(
    diretoria_regional_centro,
    tipo_escola_emef,
    subprefeitura_se,
):
    """Cria uma unidade educacional do tipo EMEF para testes."""
    return Unidadeeducacional.objects.create(
        codigo_eol="900009",
        nome="EMEF ESCOLA TESTE INATIVA",
        diretoria_regional=diretoria_regional_centro,
        tipo_escola=tipo_escola_emef,
        subprefeitura=subprefeitura_se,
        status=False,
    )


@pytest.fixture
def unidade_educacional_cemei(
    diretoria_regional_ipiranga,
    tipo_escola_cemei,
    subprefeitura_pirituba,
):
    """Cria uma unidade educacional do tipo CEMEI para testes."""
    return Unidadeeducacional.objects.create(
        codigo_eol="200002",
        nome="CEMEI ESCOLA TESTE",
        diretoria_regional=diretoria_regional_ipiranga,
        tipo_escola=tipo_escola_cemei,
        subprefeitura=subprefeitura_pirituba,
        status=True,
    )


@pytest.fixture
def resposta_api_diretor():
    """Retorna uma resposta HTTP simulada da API de diretores."""
    resposta = Mock()
    resposta.status_code = 200
    resposta.json.return_value = [
        {
            "codigoRF": "0000011",
            "nomeServidor": "Diretor Escola",
            "dataInicio": "10/18/2021 00:00:00",
            "dataFim": None,
            "cargo": "DIRETOR DE ESCOLA",
            "cdTipoFuncaoAtividade": 0,
            "estaAfastado": False,
            "funcaoExterno": 0,
            "tipoFuncaoExterno": 0,
        },
    ]

    return resposta


@pytest.fixture
def resposta_dados_complementares():
    """Retorna uma resposta HTTP simulada com dados complementares."""
    resposta = Mock()
    resposta.status_code = 200
    resposta.json.return_value = {
        "grupos": [],
        "dre": "DIRETORIA REGIONAL DE EDUCACAO",
        "codigoUe": "100001",
        "nomeUe": "EMEF Escola Teste",
        "enderecoUe": "Rua Teste, 100",
        "telefoneUe": "1122223333",
        "email": "diretor.um@email.com",
        "nome": "Diretor Escola",
        "cpf": "12345678900",
        "login": "1234567",
    }

    return resposta


@pytest.fixture
def usuario_sincronizacao(cargo_perfil_diretor):
    """Fixture de usuario ativo."""
    return Usuario.objects.create(
        username="sincronizacao_eol",
        nome="Sincronizador Dados do EOL",
        registro_funcional=None,
        cpf=None,
        cargo=cargo_perfil_diretor,
        is_active=False,
    )


@pytest.fixture
def responsavel_unidade() -> ResponsavelUnidade:
    """Cria um responsável de unidade para os testes."""
    return ResponsavelUnidade.objects.create(
        registro_funcional="000000011",
        nome="DIRETOR TESTE",
        email="responsavel.emef@teste.com",
        telefone="11999999999",
        esta_afastado=False,
    )


@pytest.fixture
def lote_centro(diretoria_regional_centro, empresa):
    """Fixture de lote."""
    lote = Lote.objects.create(
        codigo_cadastro="LOTE-001", nome="Lote Centro", empresa=empresa
    )
    LoteDiretoriaRegional.objects.create(
        lote=lote,
        diretoria_regional=diretoria_regional_centro,
    )
    return lote
