"""Testes do endpoint de criação de solicitações."""

from typing import Any

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db


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


def test_requisicao_nao_autenticada_retorna_401(
    solicitacao_payload: dict[str, Any],
) -> None:
    """Rejeita a criação sem autenticação."""
    resposta = APIClient().post(
        "/api/v1/solicitacoes-manutencao/",
        solicitacao_payload,
        format="json",
    )

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_documenta_criacao_da_solicitacao_no_schema() -> None:
    """Expõe no OpenAPI os detalhes da criação da solicitação."""
    resposta = APIClient().get("/api/v1/schema/?format=json")

    assert resposta.status_code == status.HTTP_200_OK
    operacao = resposta.json()["paths"]["/api/v1/solicitacoes-manutencao/"][
        "post"
    ]
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
        "/api/v1/solicitacoes-manutencao/?enviar=true",
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.json()
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.criado_por == usuario_ativo
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
        "/api/v1/solicitacoes-manutencao/",
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
        "/api/v1/solicitacoes-manutencao/",
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
        "/api/v1/solicitacoes-manutencao/",
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
    solicitacao_payload["servicos"][0].pop("servico")

    resposta = _postar_solicitacao(
        api_cliente,
        "/api/v1/solicitacoes-manutencao/",
        solicitacao_payload,
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    solicitacao = SolicitacaoManutencao.objects.get(codigo="0000001")
    assert solicitacao.servicos_manutencao.get().servico is None
