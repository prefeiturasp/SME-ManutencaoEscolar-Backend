"""Testes de API do código do contrato do lote."""

import pytest
from rest_framework import status

from apps.lote.models import Lote

pytestmark = pytest.mark.django_db

URL = "/api/v1/lotes/"
CODIGO = "31/SME/2021-SME/COMPS"


def _payload(empresa, diretoria, **extra):
    return {
        "nome": "Lote Novo",
        "codigo_cadastro": "LOTE-NOVO",
        "codigo_contrato": CODIGO,
        "empresa": str(empresa.uuid),
        "diretorias_regionais": [diretoria.id],
        "status": True,
        **extra,
    }


def test_cria_lote_com_codigo_contrato(
    api_cliente, empresa, diretoria_regional_centro
):
    """Cria o lote e devolve o código do contrato."""
    resposta = api_cliente.post(
        URL, _payload(empresa, diretoria_regional_centro), format="json"
    )

    assert resposta.status_code == status.HTTP_201_CREATED, resposta.content
    assert Lote.objects.get().codigo_contrato == CODIGO


def test_nao_cria_lote_sem_codigo_contrato(
    api_cliente, empresa, diretoria_regional_centro
):
    """O campo é obrigatório."""
    dados = _payload(empresa, diretoria_regional_centro)
    del dados["codigo_contrato"]

    resposta = api_cliente.post(URL, dados, format="json")

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "codigo_contrato" in resposta.json()
    assert not Lote.objects.exists()


def test_nao_cria_lote_com_codigo_contrato_invalido(
    api_cliente, empresa, diretoria_regional_centro
):
    """Rejeita caracteres fora do padrão alfanumérico."""
    resposta = api_cliente.post(
        URL,
        _payload(empresa, diretoria_regional_centro, codigo_contrato="31 #1"),
        format="json",
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "codigo_contrato" in resposta.json()


def test_atualiza_codigo_contrato_e_lista(api_cliente, lote_centro):
    """O PATCH altera o código e a listagem e o detalhe o devolvem."""
    resposta = api_cliente.patch(
        f"{URL}{lote_centro.uuid}/",
        {"codigo_contrato": "99/SME/2026"},
        format="json",
    )

    assert resposta.status_code == status.HTTP_200_OK, resposta.content
    lote_centro.refresh_from_db()
    assert lote_centro.codigo_contrato == "99/SME/2026"
    detalhe = api_cliente.get(f"{URL}{lote_centro.uuid}/").json()
    assert detalhe["codigo_contrato"] == "99/SME/2026"
    listagem = api_cliente.get(URL).json()["results"][0]
    assert listagem["codigo_contrato"] == "99/SME/2026"


def test_lote_antigo_sem_codigo_exige_preenchimento_ao_editar(
    api_cliente, lote_centro
):
    """Lote legado (sem código) só é editado quando o código é informado."""
    Lote.objects.filter(pk=lote_centro.pk).update(codigo_contrato="")

    sem_codigo = api_cliente.patch(
        f"{URL}{lote_centro.uuid}/", {"nome": "Outro nome"}, format="json"
    )
    com_codigo = api_cliente.patch(
        f"{URL}{lote_centro.uuid}/",
        {"nome": "Outro nome", "codigo_contrato": CODIGO},
        format="json",
    )

    assert sem_codigo.status_code == status.HTTP_400_BAD_REQUEST
    assert "codigo_contrato" in sem_codigo.json()
    assert com_codigo.status_code == status.HTTP_200_OK, com_codigo.content
