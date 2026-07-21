"""Testes para as views da aplicação Fornecedor."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status

from apps.fornecedor.models import Fornecedor
from apps.fornecedor.services.fornecedor_service import (
    FornecedorCnpjDuplicadoError,
)

pytestmark = pytest.mark.django_db


def test_listagem_retorna_lista_vazia(api_client):
    """
    Testa a listagem de fornecedores via API.

    Verifica se o retorno é uma lista vazia.
    """
    response = api_client.get("/api/v1/fornecedores/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_criacao_retorna_fornecedor(api_client, fornecedor_payload_valido):
    """
    Testa a criação de um fornecedor via API.

    Verifica se o retorno é correto.
    """
    fornecedor = Fornecedor(**fornecedor_payload_valido)

    def criar(dados):
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
