"""Testes das views do domínio Profissional."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.pagination import PaginacaoPadrao
from apps.profissional.api.views import ProfissionalViewSet
from apps.profissional.models import FuncaoProfissional, Profissional
from apps.profissional.serializers.profissional_serializers import (
    ProfissionalListSerializer,
    ProfissionalSerializer,
)

pytestmark = pytest.mark.django_db


def test_cria_profissional_com_funcao(
    api_cliente, profissional_payload, usuario_ativo, cargo_profissional
):
    """Cria o profissional com sua função e registra a autoria."""
    cargo_profissional.exige_documento = False
    cargo_profissional.save(update_fields=["exige_documento"])
    profissional_payload["funcoes"][0]["documentos"] = []
    resposta = api_cliente.post(
        "/api/v1/profissionais/", profissional_payload, format="json"
    )

    assert resposta.status_code == status.HTTP_201_CREATED
    profissional = Profissional.objects.get(cpf="12345678901")
    funcao = profissional.funcoes.get()
    assert profissional.criado_por == usuario_ativo
    assert not funcao.documentos.exists()


def test_rejeita_cpf_duplicado(
    api_cliente, profissional_payload, cargo_profissional
):
    """Não permite dois profissionais ativos com o mesmo CPF."""
    cargo_profissional.exige_documento = False
    cargo_profissional.save(update_fields=["exige_documento"])
    profissional_payload["funcoes"][0]["documentos"] = []
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


def test_view_usa_serializer_de_listagem():
    """Seleciona o serializer resumido na listagem."""
    view = ProfissionalViewSet()
    view.action = "list"

    assert view.get_serializer_class() is ProfissionalListSerializer


def test_view_usa_serializer_de_detalhes_para_outras_acoes():
    """Seleciona o serializer detalhado fora da criação e listagem."""
    view = ProfissionalViewSet()
    view.action = "retrieve"

    assert view.get_serializer_class() is ProfissionalSerializer


def test_view_configura_listagem_paginada():
    """Configura filtros e paginação padrão para a listagem."""
    view = ProfissionalViewSet()

    assert view.pagination_class is PaginacaoPadrao
    assert view.http_method_names == ["get", "post", "options"]


def test_lista_profissionais_com_funcoes(
    api_cliente, cargo_profissional, usuario_ativo
):
    """Lista profissionais paginados com os dados de suas funções."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
        criado_por=usuario_ativo,
    )
    FuncaoProfissional.objects.create(
        profissional=profissional,
        cargo=cargo_profissional,
        criado_por=usuario_ativo,
    )

    resposta = api_cliente.get("/api/v1/profissionais/")

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "uuid": str(profissional.uuid),
                "nome": "José da Silva",
                "cpf": "12345678901",
                "rg": "123456789",
                "status": True,
                "funcoes": ["Eletricista"],
            }
        ],
    }


@pytest.mark.parametrize(
    ("parametros", "nome_esperado"),
    [
        ({"nome": "maria"}, "Maria Souza"),
        ({"cpf": "222"}, "Maria Souza"),
        ({"rg": "444"}, "Maria Souza"),
        ({"status": "false"}, "Maria Souza"),
    ],
)
def test_lista_profissionais_com_filtros(
    api_cliente, parametros, nome_esperado
):
    """Filtra a listagem por nome, CPF, RG e status."""
    Profissional.objects.create(
        nome="José da Silva", cpf="11111111111", rg="333333333", status=True
    )
    Profissional.objects.create(
        nome="Maria Souza", cpf="22222222222", rg="444444444", status=False
    )

    resposta = api_cliente.get("/api/v1/profissionais/", parametros)

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 1
    assert resposta.json()["results"][0]["nome"] == nome_esperado


def test_lista_profissionais_filtra_funcao_pelo_nome_do_cargo(
    api_cliente, cargo_profissional
):
    """Filtra profissionais pelo nome parcial e sem caixa do cargo."""
    eletricista = Profissional.objects.create(
        nome="José da Silva", cpf="11111111111", rg="333333333"
    )
    Profissional.objects.create(
        nome="Maria Souza", cpf="22222222222", rg="444444444"
    )
    FuncaoProfissional.objects.create(
        profissional=eletricista,
        cargo=cargo_profissional,
    )

    resposta = api_cliente.get("/api/v1/profissionais/", {"funcao": "ELETRIC"})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json()["count"] == 1
    assert resposta.json()["results"][0]["nome"] == "José da Silva"


def test_listagem_sem_autenticacao_retorna_401():
    """Protege a listagem contra acesso não autenticado."""
    resposta = APIClient().get("/api/v1/profissionais/")

    assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


def test_criacao_converte_validation_error_do_django(
    api_cliente, profissional_payload
):
    """Converte erros do serviço em resposta de validação da API."""
    profissional_payload["funcoes"][0]["documentos"] = []
    with patch(
        "apps.profissional.api.views.ProfissionalService.criar",
        side_effect=ValidationError({"cpf": ["CPF inválido"]}),
    ):
        resposta = api_cliente.post(
            "/api/v1/profissionais/", profissional_payload, format="json"
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["cpf"] == ["CPF inválido"]
