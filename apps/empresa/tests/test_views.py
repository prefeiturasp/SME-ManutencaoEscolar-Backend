"""Testes para as views da aplicação Empresa."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from apps.empresa.exceptions import (
    EmpresaCnpjDuplicadoError,
)
from apps.empresa.models import Empresa, ResponsavelTecnico

pytestmark = pytest.mark.django_db


def test_requisicao_nao_autenticada_retorna_401(
    empresa_payload_valido,
):
    """Testa se requisições sem autenticação são rejeitadas."""
    response = APIClient().post(
        "/api/v1/empresas/",
        empresa_payload_valido,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_criacao_retorna_empresa(
    api_client, empresa_payload_valido_com_responsaveis, usuario_ativo
):
    """
    Testa a criação de uma empresa via API.

    Verifica se o retorno é correto.
    """
    empresa = {
        **empresa_payload_valido_com_responsaveis,
        "id": 1,
        "uuid": "7ef06bb8-418f-43d1-bfe8-c392f13a2b1f",
        "status": True,
    }

    def criar(dados, usuario):
        """Simula o retorno do serviço durante a criação da empresa."""
        assert dados == empresa_payload_valido_com_responsaveis
        assert usuario == usuario_ativo
        return empresa

    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.criar",
        side_effect=criar,
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido_com_responsaveis,
            format="json",
        )

    nome_esperado = empresa_payload_valido_com_responsaveis["nome"]
    cnpj_esperado = empresa_payload_valido_com_responsaveis["cnpj"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["nome"] == nome_esperado
    assert response.json()["cnpj"] == cnpj_esperado


def test_criacao_mapeia_cnpj_duplicado_para_erro_de_validacao(
    api_client, empresa_payload_valido_com_responsaveis
):
    """
    Testa se a criação de uma empresa.

    Mapeia o erro de CNPJ duplicado para erro de validação.
    """
    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.criar",
        side_effect=EmpresaCnpjDuplicadoError(
            "Já existe uma empresa cadastrada com este CNPJ."
        ),
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido_com_responsaveis,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["cnpj"] == (
        "Já existe uma empresa cadastrada com este CNPJ."
    )


def test_criacao_mapeia_validation_error_do_django(
    api_client, empresa_payload_valido_com_responsaveis
):
    """
    Testa criação de uma empresa.

    Mapeia o ValidationError do Django.
    """
    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.criar",
        side_effect=ValidationError({"nome": ["nome inválido"]}),
    ):
        response = api_client.post(
            "/api/v1/empresas/",
            empresa_payload_valido_com_responsaveis,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["nome"][0] == "nome inválido"


def test_atualizacao_retorna_empresa(
    api_client,
    empresa_payload_valido,
    empresa_payload_valido_com_responsaveis,
    usuario_ativo,
):
    """
    Testa a atualização de uma empresa via API (PUT).

    Verifica se o retorno é correto.
    """
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)
    payload_atualizado = {
        **empresa_payload_valido_com_responsaveis,
        "nome": "Novo Nome",
    }
    empresa_atualizada = {
        **payload_atualizado,
        "id": empresa_existente.id,
        "uuid": str(empresa_existente.uuid),
    }

    def atualizar(instance, dados, usuario):
        """Simula o retorno do serviço durante a atualização da empresa."""
        assert instance == empresa_existente
        assert dados == payload_atualizado
        assert usuario == usuario_ativo
        return empresa_atualizada

    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.atualizar",
        side_effect=atualizar,
    ):
        response = api_client.put(
            f"/api/v1/empresas/{empresa_existente.uuid}/",
            payload_atualizado,
            format="json",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome"] == "Novo Nome"


def test_atualizacao_sincroniza_responsaveis_tecnicos(
    api_client, empresa_payload_valido, usuario_ativo
):
    """PUT deve atualizar a empresa e sincronizar os responsáveis por tipo."""
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)
    ResponsavelTecnico.objects.create(
        empresa=empresa_existente,
        nome="Preposto Antigo",
        tipo="preposto",
        email="preposto.antigo@email.com",
        telefone="11987654321",
    )
    ResponsavelTecnico.objects.create(
        empresa=empresa_existente,
        nome="Engenheiro Antigo",
        tipo="engenheiro_civil",
        email="engenheiro.antigo@email.com",
        telefone="11987654321",
    )
    payload = {
        **empresa_payload_valido,
        "nome": "Novo Nome",
        "responsaveis_tecnicos": [
            {
                "tipo": "preposto",
                "nome": "Preposto Novo",
                "email": "preposto.novo@email.com",
                "telefone": "11987654321",
            }
        ],
    }

    response = api_client.put(
        f"/api/v1/empresas/{empresa_existente.uuid}/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome"] == "Novo Nome"
    tipos = {
        responsavel["tipo"]
        for responsavel in response.json()["responsaveis_tecnicos"]
    }
    assert tipos == {"preposto"}

    empresa_existente.refresh_from_db()
    assert empresa_existente.nome == "Novo Nome"
    responsaveis = ResponsavelTecnico.objects.filter(empresa=empresa_existente)
    assert responsaveis.count() == 1
    assert responsaveis.get().nome == "Preposto Novo"


def test_atualizacao_mapeia_cnpj_duplicado_para_erro_de_validacao(
    api_client, empresa_payload_valido, empresa_payload_valido_com_responsaveis
):
    """
    Testa se a atualização de uma empresa.

    Mapeia o erro de CNPJ duplicado para erro de validação.
    """
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)

    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.atualizar",
        side_effect=EmpresaCnpjDuplicadoError(
            "Já existe uma empresa cadastrada com este CNPJ."
        ),
    ):
        response = api_client.put(
            f"/api/v1/empresas/{empresa_existente.uuid}/",
            empresa_payload_valido_com_responsaveis,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["cnpj"] == (
        "Já existe uma empresa cadastrada com este CNPJ."
    )


def test_atualizacao_mapeia_validation_error_do_django(
    api_client, empresa_payload_valido, empresa_payload_valido_com_responsaveis
):
    """
    Testa atualização de uma empresa.

    Mapeia o ValidationError do Django.
    """
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)

    with patch(
        "apps.empresa.api.views.empresa_views.EmpresaService.atualizar",
        side_effect=ValidationError({"nome": ["nome inválido"]}),
    ):
        response = api_client.put(
            f"/api/v1/empresas/{empresa_existente.uuid}/",
            empresa_payload_valido_com_responsaveis,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["nome"][0] == "nome inválido"


def test_atualizacao_de_empresa_inexistente_retorna_404(
    api_client, empresa_payload_valido
):
    """Testa se a atualização de uma empresa inexistente retorna 404."""
    response = api_client.put(
        "/api/v1/empresas/7ef06bb8-418f-43d1-bfe8-c392f13a2b1f/",
        empresa_payload_valido,
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_recuperacao_retorna_empresa_por_uuid(
    api_client, empresa_payload_valido
):
    """Testa se a recuperação de uma empresa via API é feita pelo uuid."""
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)

    response = api_client.get(f"/api/v1/empresas/{empresa_existente.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uuid"] == str(empresa_existente.uuid)
    assert response.json()["nome"] == empresa_payload_valido["nome"]


def test_recuperacao_de_empresa_inexistente_retorna_404(api_client):
    """Testa se a recuperação de uma empresa inexistente retorna 404."""
    response = api_client.get(
        "/api/v1/empresas/7ef06bb8-418f-43d1-bfe8-c392f13a2b1f/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


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


def test_remocao_deleta_empresa_e_some_da_listagem(
    api_client, empresa_payload_valido
):
    """Testa se a remoção via API faz a exclusão lógica da empresa."""
    empresa_existente = Empresa.objects.create(**empresa_payload_valido)

    response = api_client.delete(f"/api/v1/empresas/{empresa_existente.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Empresa.objects.filter(uuid=empresa_existente.uuid).exists()


def test_remocao_de_empresa_inexistente_retorna_404(api_client):
    """Testa se a remoção de uma empresa inexistente retorna 404."""
    response = api_client.delete(
        "/api/v1/empresas/7ef06bb8-418f-43d1-bfe8-c392f13a2b1f/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


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
