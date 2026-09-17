"""Testes das views do domínio Profissional."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from apps.profissional.api.views import ProfissionalViewSet
from apps.profissional.models import Profissional

pytestmark = pytest.mark.django_db


def test_cria_profissional_com_funcao_e_documento(
    api_cliente, profissional_payload, usuario_ativo
):
    """Cria todo o agregado e registra a autoria."""
    resposta = api_cliente.post(
        "/api/v1/profissionais/", profissional_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    profissional = Profissional.objects.get(cpf="12345678901")
    funcao = profissional.funcoes.get()
    assert profissional.criado_por == usuario_ativo
    assert funcao.documentos.get().nome == "Certificado NR10"


def test_rejeita_cpf_duplicado(api_cliente, profissional_payload):
    """Não permite dois profissionais ativos com o mesmo CPF."""
    api_cliente.post(
        "/api/v1/profissionais/", profissional_payload, format="json"
    )
    payload = {**profissional_payload, "rg": "987654321"}

    resposta = api_cliente.post(
        "/api/v1/profissionais/", payload, format="json"
    )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST


def test_requisicao_sem_autenticacao_retorna_401(profissional_payload):
    """Protege o endpoint contra acesso não autenticado."""
    resposta = APIClient().post(
        "/api/v1/profissionais/", profissional_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_view_usa_serializer_de_leitura_para_outras_acoes():
    """Seleciona o serializer de leitura fora da criação."""
    view = ProfissionalViewSet()
    view.action = "list"

    assert view.get_serializer_class().__name__ == "ProfissionalSerializer"


def test_criacao_converte_validation_error_do_django(
    api_cliente, profissional_payload
):
    """Converte erros do serviço em resposta de validação da API."""
    with patch(
        "apps.profissional.api.views.ProfissionalService.criar",
        side_effect=ValidationError({"cpf": ["CPF inválido"]}),
    ):
        resposta = api_cliente.post(
            "/api/v1/profissionais/", profissional_payload, format="json"
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["cpf"] == ["CPF inválido"]
