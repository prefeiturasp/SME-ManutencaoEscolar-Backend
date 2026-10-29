"""Testes do endpoint de criação de solicitações."""

from datetime import datetime
from typing import Any

import pytest
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from apps.solicitacao_manutencao.api.views import SolicitacaoManutencaoViewSet
from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.serializers import (
    SolicitacaoManutencaoCriarSerializer,
    SolicitacaoManutencaoListSerializer,
)
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db

URL_SOLICITACAO_UE = "/api/v1/solicitacoes-manutencao/solicitacao-ue/"
URL_SOLICITACOES = "/api/v1/solicitacoes-manutencao/"
URL_SITUACOES = "/api/v1/solicitacoes-manutencao/situacoes/"
URL_FASES = "/api/v1/solicitacoes-manutencao/fases/"
URL_TIPOS_ATENDIMENTO = "/api/v1/solicitacoes-manutencao/tipos-atendimento/"


def _postar_solicitacao(
    cliente: APIClient,
    url: str,
    payload: dict[str, Any],
) -> Any:
    """Envia uma solicitação com seus arquivos em formato multipart."""
    dados = {
        chave: valor for chave, valor in payload.items() if chave != "servicos"
    }
    for indice_servico, servico in enumerate(payload["servicos"]):
        for chave, valor in servico.items():
            if chave != "arquivos":
                dados[f"servicos[{indice_servico}]{chave}"] = valor
        for indice_arquivo, arquivo in enumerate(servico.get("arquivos", [])):
            for chave, valor in arquivo.items():
                if hasattr(valor, "seek"):
                    valor.seek(0)
                dados[
                    "servicos"
                    f"[{indice_servico}]arquivos[{indice_arquivo}]{chave}"
                ] = valor

    return cliente.post(url, dados, format="multipart")


def test_seleciona_serializer_conforme_acao() -> None:
    """Usa um serializer resumido somente na listagem."""
    view = SolicitacaoManutencaoViewSet()
    view.action = "list"
    assert view.get_serializer_class() is SolicitacaoManutencaoListSerializer

    view.action = "solicitacao_ue"
    assert view.get_serializer_class() is SolicitacaoManutencaoCriarSerializer


def test_lista_situacoes_da_solicitacao(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos das situações da solicitação."""
    resposta = api_cliente.get(URL_SITUACOES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()[0] == {
        "value": "nao_enviado_dre",
        "label": "Não enviada para a DRE",
    }
    assert len(resposta.json()) == 9


def test_lista_fases_da_solicitacao(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos das fases da solicitação."""
    resposta = api_cliente.get(URL_FASES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == [
        {"value": "solicitacao", "label": "Solicitação"},
        {"value": "vistoria", "label": "Vistoria"},
        {"value": "execucao", "label": "Execução"},
    ]


def test_lista_tipos_atendimento(api_cliente: APIClient) -> None:
    """Retorna os valores e rótulos dos tipos de atendimento."""
    resposta = api_cliente.get(URL_TIPOS_ATENDIMENTO)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == [
        {"value": "comum", "label": "Comum"},
        {"value": "urgente", "label": "Urgente"},
    ]


def test_documenta_choices_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI a consulta de cada escolha da solicitação."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacoes = {
        url: resposta.json()["paths"][url]["get"]
        for url in (URL_SITUACOES, URL_FASES, URL_TIPOS_ATENDIMENTO)
    }
    assert operacoes[URL_SITUACOES]["operationId"] == (
        "listarSituacoesSolicitacaoManutencao"
    )
    assert operacoes[URL_FASES]["operationId"] == (
        "listarFasesSolicitacaoManutencao"
    )
    assert operacoes[URL_TIPOS_ATENDIMENTO]["operationId"] == (
        "listarTiposAtendimentoSolicitacaoManutencao"
    )
    assert all(
        set(operacao["responses"]) == {"200", "401", "500"}
        for operacao in operacoes.values()
    )


def test_lista_solicitacoes_paginadas(
    api_cliente_ue: APIClient,
    unidade_educacional_emef: Any,
    usuario_ue: Usuario,
    usuario_inativo: Usuario,
) -> None:
    """Lista somente solicitações criadas pelo usuário autenticado."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ue,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_inativo,
    )

    resposta = api_cliente_ue.get(URL_SOLICITACOES)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "uuid": str(solicitacao.uuid),
                "codigo": "0000001",
                "tipo_atendimento": "urgente",
                "situacao": "nao_enviado_dre",
                "data_envio": None,
                "fase": "solicitacao",
            }
        ],
    }


@pytest.mark.parametrize(
    ("parametros", "codigo_esperado"),
    [
        ({"codigo": "0002"}, "0000002"),
        ({"tipo_atendimento": "comum"}, "0000002"),
        ({"situacao": "aguardando_analise_dre"}, "0000002"),
    ],
)
def test_filtra_listagem_de_solicitacoes(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
    parametros: dict[str, str],
    codigo_esperado: str,
) -> None:
    """Filtra a listagem pelos dados da solicitação."""
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        situacao="aguardando_analise_dre",
        criado_por=usuario_ativo,
    )

    resposta = api_cliente.get(URL_SOLICITACOES, parametros)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 1
    assert resposta.json()["results"][0]["codigo"] == codigo_esperado


@pytest.mark.parametrize(
    ("campo", "valores"),
    [
        ("tipo_atendimento", "comum,urgente"),
        ("situacao", "nao_enviado_dre,aguardando_analise_dre"),
        ("fase", "solicitacao,vistoria"),
    ],
)
def test_filtra_listagem_de_solicitacoes_por_multiplos_valores(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
    campo: str,
    valores: str,
) -> None:
    """Filtra a listagem por múltiplos valores do mesmo campo."""
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="urgente",
        unidade_educacional=unidade_educacional_emef,
        criado_por=usuario_ativo,
    )
    SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional_emef,
        situacao="aguardando_analise_dre",
        fase="vistoria",
        criado_por=usuario_ativo,
    )

    resposta = api_cliente.get(URL_SOLICITACOES, {campo: valores})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 2


def test_filtra_listagem_por_intervalo_de_data_envio(
    api_cliente: APIClient,
    unidade_educacional_emef: Any,
    usuario_ativo: Usuario,
) -> None:
    """Filtra solicitações cuja data de envio esteja no intervalo."""
    for codigo, data_envio in (
        ("0000001", datetime(2026, 10, 9, 23, 59)),
        ("0000002", datetime(2026, 10, 10, 12)),
        ("0000003", datetime(2026, 10, 20, 23, 59)),
        ("0000004", datetime(2026, 10, 21)),
    ):
        SolicitacaoManutencao.objects.create(
            codigo=codigo,
            tipo_atendimento="comum",
            unidade_educacional=unidade_educacional_emef,
            data_envio=timezone.make_aware(data_envio),
            criado_por=usuario_ativo,
        )

    resposta = api_cliente.get(
        URL_SOLICITACOES,
        {
            "data_envio_after": "2026-10-10",
            "data_envio_before": "2026-10-20",
        },
    )

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 2
    assert {item["codigo"] for item in resposta.json()["results"]} == {
        "0000002",
        "0000003",
    }


def test_listagem_de_solicitacoes_exige_autenticacao() -> None:
    """Protege a listagem contra acesso não autenticado."""
    resposta = APIClient().get(URL_SOLICITACOES)

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_documenta_listagem_de_solicitacoes_no_schema() -> None:
    """Expõe a listagem paginada e seus filtros no OpenAPI."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"][URL_SOLICITACOES]["get"]
    assert operacao["operationId"] == "listarSolicitacoesManutencao"
    assert operacao["summary"] == "Lista as solicitações de manutenção"
    assert {parametro["name"] for parametro in operacao["parameters"]} >= {
        "codigo",
        "tipo_atendimento",
        "situacao",
        "fase",
        "data_envio",
    }
    assert set(operacao["responses"]) == {"200", "401", "500"}


def test_requisicao_nao_autenticada_retorna_401(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita a criação sem autenticação."""
    resposta = APIClient().post(
        URL_SOLICITACAO_UE,
        solicitacao_payload,
        format="json",
    )

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_solicitacao_ue_rejeita_usuario_nao_identificado() -> None:
    """Impede a criação quando a requisição não identifica um usuário."""
    requisicao = Request(APIRequestFactory().post(URL_SOLICITACAO_UE))
    requisicao.user = AnonymousUser()
    view = SolicitacaoManutencaoViewSet()

    with pytest.raises(NotAuthenticated, match="Usuário não identificado"):
        SolicitacaoManutencaoViewSet.solicitacao_ue(view, requisicao)


def test_documenta_criacao_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI os detalhes da criação da solicitação."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"][
        "/api/v1/solicitacoes-manutencao/solicitacao-ue/"
    ]["post"]
    assert operacao["operationId"] == "criarSolicitacaoManutencao"
    assert operacao["summary"] == "Cria uma solicitação de manutenção"
    assert operacao["parameters"][0]["name"] == "enviar"
    assert set(operacao["responses"]) == {"201", "400", "401", "500"}


def test_cria_solicitacao_com_servicos(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
    usuario_ativo: Usuario,
) -> None:
    """Cria a solicitação e seus serviços em uma única requisição."""
    resposta = _postar_solicitacao(
        api_cliente,
        f"{URL_SOLICITACAO_UE}?enviar=true",
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.json()
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.criado_por == usuario_ativo
    assert solicitacao.solicitante == "ue"
    assert solicitacao.data_envio is not None
    assert solicitacao.servicos_manutencao.count() == 1
    assert solicitacao.servicos_manutencao.get().criado_por == usuario_ativo
    assert resposta.json()["servicos"][0]["local_reparo"] == "Cozinha"
    assert len(resposta.json()["servicos"][0]["arquivos"]) == 1


def test_cria_solicitacao_sem_enviar_para_dre(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Mantém a solicitação sem envio quando o parâmetro não é informado."""
    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.situacao == "nao_enviado_dre"
    assert solicitacao.data_envio is None


def test_exige_ao_menos_um_servico(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Não cria uma solicitação sem serviços de manutenção."""
    solicitacao_payload["servicos"] = []

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert SolicitacaoManutencao.objects.count() == 0


def test_exige_arquivos_em_cada_servico(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Não cria uma solicitação quando arquivos não são informados."""
    solicitacao_payload["servicos"][0].pop("arquivos")

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "arquivos" in resposta.json()["servicos"]["0"]
    assert SolicitacaoManutencao.objects.count() == 0


def test_cria_solicitacao_sem_servico_catalogado(
    api_cliente: APIClient,
    solicitacao_payload: dict[str, Any],
) -> None:
    """Cria uma solicitação sem vincular um serviço catalogado."""
    dados_servico = solicitacao_payload["servicos"][0]
    dados_servico.pop("servico")
    dados_servico["servico_especifico"] = "Troca de disjuntor"

    resposta = _postar_solicitacao(
        api_cliente,
        URL_SOLICITACAO_UE,
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.servicos_manutencao.get().servico is None