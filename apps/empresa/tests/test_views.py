"""Testes para as views da aplicação Empresa."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status

from apps.empresa.exceptions import (
    EmpresaCnpjDuplicadoError,
)
from apps.empresa.models import Empresa

pytestmark = pytest.mark.django_db


def test_criacao_retorna_empresa(api_client, empresa_payload_valido):
    """
    Testa a criação de uma empresa via API.

    Verifica se o retorno é correto.
    """
    empresa = {
        **empresa_payload_valido,
        "id": 1,
        "uuid": "7ef06bb8-418f-43d1-bfe8-c392f13a2b1f",
        "status": True,
    }

    def criar(dados):
        """Simula o retorno do serviço durante a criação da empresa."""
        assert dados == empresa_payload_valido
        return empresa

    with patch(
        "apps.empresa.api.views.EmpresaService.criar",
        side_effect=criar,
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["nome"] == empresa_payload_valido["nome"]
    assert response.json()["cnpj"] == empresa_payload_valido["cnpj"]


def test_criacao_mapeia_cnpj_duplicado_para_erro_de_validacao(
    api_client, empresa_payload_valido
):
    """
    Testa se a criação de uma empresa.

    Mapeia o erro de CNPJ duplicado para erro de validação.
    """
    with patch(
        "apps.empresa.api.views.EmpresaService.criar",
        side_effect=EmpresaCnpjDuplicadoError(
            "Já existe uma empresa cadastrada com este CNPJ."
        ),
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["cnpj"] == (
        "Já existe uma empresa cadastrada com este CNPJ."
    )


def test_criacao_mapeia_validation_error_do_django(
    api_client, empresa_payload_valido
):
    """
    Testa criação de uma empresa.

    Mapeia o ValidationError do Django.
    """
    with patch(
        "apps.empresa.api.views.EmpresaService.criar",
        side_effect=ValidationError({"nome": ["nome inválido"]}),
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["nome"][0] == "nome inválido"


def test_listagem_retorna_empresas_cadastrados(
    api_client, empresa_payload_valido
):
    """Testa se a listagem retorna as empresas cadastradas."""
    Empresa.objects.create(**empresa_payload_valido)

    response = api_client.get("/api/v1/empresas/")

    dados = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert dados["count"] == 1
    assert len(dados["results"]) == 1
    assert dados["results"][0]["nome"] == empresa_payload_valido["nome"]


def test_listagem_filtra_por_nome(api_client, empresa_payload_valido):
    """Testa se a listagem filtra empresas pelo nome."""
    Empresa.objects.create(**empresa_payload_valido)
    Empresa.objects.create(
        **{
            **empresa_payload_valido,
            "nome": "Outra Empresa",
            "cnpj": "98765432109876",
        }
    )

    response = api_client.get(
        "/api/v1/empresas/",
        {"nome": "Exemplo"},
    )

    dados = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert dados["count"] == 1
    assert len(dados["results"]) == 1
    assert dados["results"][0]["nome"] == empresa_payload_valido["nome"]


def test_listagem_filtra_por_status(
    api_client,
    empresa_payload_valido,
):
    """Testa se a listagem filtra empresas pelo status."""
    Empresa.objects.create(
        **empresa_payload_valido,
        status=True,
    )
    Empresa.objects.create(
        **{
            **empresa_payload_valido,
            "cnpj": "98765432109876",
            "status": False,
        }
    )

    response = api_client.get(
        "/api/v1/empresas/",
        {"status": "false"},
    )

    dados = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert dados["count"] == 1
    assert len(dados["results"]) == 1
    assert dados["results"][0]["status"] is False
    assert dados["results"][0]["cnpj"] == "98765432109876"
