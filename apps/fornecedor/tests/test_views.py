"""Testes para as views da aplicação Fornecedor."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status

from apps.fornecedor.exceptions import (
    FornecedorCnpjDuplicadoError,
)

pytestmark = pytest.mark.django_db


def test_criacao_retorna_fornecedor(api_client, fornecedor_payload_valido):
    """
    Testa a criação de um fornecedor via API.

    Verifica se o retorno é correto.
    """
    fornecedor = {
        **fornecedor_payload_valido,
        "id": 1,
        "uuid": "7ef06bb8-418f-43d1-bfe8-c392f13a2b1f",
        "status": True,
    }

    def criar(dados):
        """Simula o retorno do serviço durante a criação do fornecedor."""
        assert dados == fornecedor_payload_valido
        return fornecedor

    with patch(
        "apps.fornecedor.api.views.FornecedorService.criar",
        side_effect=criar,
    ):
        response = api_client.post(
            "/api/v1/fornecedores/",
            fornecedor_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["nome"] == fornecedor_payload_valido["nome"]
    assert response.json()["cnpj"] == fornecedor_payload_valido["cnpj"]


def test_criacao_mapeia_cnpj_duplicado_para_erro_de_validacao(
    api_client, fornecedor_payload_valido
):
    """
    Testa se a criação de um fornecedor.

    Mapeia o erro de CNPJ duplicado para erro de validação.
    """
    with patch(
        "apps.fornecedor.api.views.FornecedorService.criar",
        side_effect=FornecedorCnpjDuplicadoError(
            "Já existe um fornecedor cadastrado com este CNPJ."
        ),
    ):
        response = api_client.post(
            "/api/v1/fornecedores/",
            fornecedor_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["cnpj"] == (
        "Já existe um fornecedor cadastrado com este CNPJ."
    )


def test_criacao_mapeia_validation_error_do_django(
    api_client, fornecedor_payload_valido
):
    """
    Testa criação de um fornecedor.

    Mapeia o ValidationError do Django.
    """
    with patch(
        "apps.fornecedor.api.views.FornecedorService.criar",
        side_effect=ValidationError({"nome": ["nome inválido"]}),
    ):
        response = api_client.post(
            "/api/v1/fornecedores/",
            fornecedor_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["nome"][0] == "nome inválido"
