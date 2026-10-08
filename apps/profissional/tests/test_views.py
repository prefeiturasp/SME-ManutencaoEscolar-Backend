"""Testes das views do domínio Profissional."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.constants import TipoArquivo
from apps.core.exceptions import AnexoArquivoError
from apps.core.pagination import PaginacaoPadrao
from apps.profissional.api.views import ProfissionalViewSet
from apps.profissional.models import FuncaoProfissional, Profissional
from apps.profissional.serializers.profissional_serializers import (
    ProfissionalCriarAtualizarSerializer,
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


def test_view_usa_serializer_de_escrita_na_atualizacao():
    """Seleciona o serializer de escrita na atualização integral."""
    view = ProfissionalViewSet()
    view.action = "update"

    assert view.get_serializer_class() is ProfissionalCriarAtualizarSerializer


def test_view_configura_listagem_paginada():
    """Configura filtros e paginação padrão para a listagem."""
    view = ProfissionalViewSet()

    assert view.pagination_class is PaginacaoPadrao
    assert view.http_method_names == [
        "get",
        "post",
        "put",
        "delete",
        "options",
    ]


def test_atualiza_profissional_com_funcoes(
    api_cliente, cargo_profissional, usuario_ativo
):
    """PUT atualiza o profissional e preserva a função pelo UUID."""
    cargo_profissional.exige_documento = False
    cargo_profissional.save(update_fields=["exige_documento"])
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional,
        cargo=cargo_profissional,
    )

    resposta = api_cliente.put(
        f"/api/v1/profissionais/{profissional.uuid}/",
        {
            "nome": "José Atualizado",
            "cpf": profissional.cpf,
            "rg": profissional.rg,
            "status": False,
            "funcoes": [
                {
                    "uuid": str(funcao.uuid),
                    "uuid_cargo": str(cargo_profissional.uuid),
                    "documentos": [],
                }
            ],
        },
        format="json",
    )

    profissional.refresh_from_db()
    funcao.refresh_from_db()
    assert resposta.status_code == status.HTTP_200_OK
    assert profissional.nome == "José Atualizado"
    assert profissional.status is False
    assert profissional.atualizado_por == usuario_ativo
    assert funcao.atualizado_por == usuario_ativo


def test_atualiza_profissional_preservando_documento_existente(
    api_cliente, cargo_profissional
):
    """PUT preserva documento informado por UUID sem exigir novo arquivo."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional,
        cargo=cargo_profissional,
    )
    documento = funcao.documentos.create(
        nome_original="NR10.pdf",
        arquivo=SimpleUploadedFile("NR10.pdf", b"conteudo"),
        tipo=TipoArquivo.DOCUMENTO,
        tipo_mime="application/pdf",
        tamanho_bytes=len(b"conteudo"),
    )

    resposta = api_cliente.put(
        f"/api/v1/profissionais/{profissional.uuid}/",
        {
            "nome": "José Atualizado",
            "cpf": profissional.cpf,
            "rg": profissional.rg,
            "status": profissional.status,
            "funcoes": [
                {
                    "uuid": str(funcao.uuid),
                    "uuid_cargo": str(cargo_profissional.uuid),
                    "documentos": [{"uuid": str(documento.uuid)}],
                }
            ],
        },
        format="json",
    )

    assert resposta.status_code == status.HTTP_200_OK, resposta.json()
    assert funcao.documentos.filter(uuid=documento.uuid).exists()


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
    funcao_profissional = FuncaoProfissional.objects.create(
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
                "funcoes": [
                    {
                        "nome": "Eletricista",
                        "uuid": str(funcao_profissional.uuid),
                    }
                ],
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


def test_lista_profissionais_filtra_funcao_pelo_uuid_do_cargo(
    api_cliente, cargo_profissional
):
    """Filtra profissionais pelo UUID do cargo."""
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

    resposta = api_cliente.get(
        "/api/v1/profissionais/", {"funcao": str(cargo_profissional.uuid)}
    )

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


def test_criacao_converte_erro_de_anexo(api_cliente, profissional_payload):
    """Converte arquivo inválido em resposta de validação da API."""
    profissional_payload["funcoes"][0]["documentos"] = []
    erro = AnexoArquivoError(
        title="Tipo de arquivo não permitido",
        detail="O tipo de arquivo informado não é permitido.",
    )
    with patch(
        "apps.profissional.api.views.ProfissionalService.criar",
        side_effect=erro,
    ):
        resposta = api_cliente.post(
            "/api/v1/profissionais/", profissional_payload, format="json"
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "title": erro.title,
        "detail": erro.detail,
    }


def test_atualizacao_converte_validation_error_do_django(
    api_cliente, cargo_profissional
):
    """Converte erros da atualização em resposta de validação da API."""
    cargo_profissional.exige_documento = False
    cargo_profissional.save(update_fields=["exige_documento"])
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )
    funcao = FuncaoProfissional.objects.create(
        profissional=profissional,
        cargo=cargo_profissional,
    )

    with patch(
        "apps.profissional.api.views.ProfissionalService.atualizar",
        side_effect=ValidationError({"cpf": ["CPF inválido"]}),
    ):
        resposta = api_cliente.put(
            f"/api/v1/profissionais/{profissional.uuid}/",
            {
                "nome": profissional.nome,
                "cpf": profissional.cpf,
                "rg": profissional.rg,
                "status": profissional.status,
                "funcoes": [
                    {
                        "uuid": str(funcao.uuid),
                        "uuid_cargo": str(cargo_profissional.uuid),
                        "documentos": [],
                    }
                ],
            },
            format="json",
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json()["cpf"] == ["CPF inválido"]


def test_remocao_deleta_profissional_e_some_da_listagem(
    api_cliente,
):
    """Testa se a remoção via API faz a exclusão lógica do profissional."""
    prof_existente = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )

    response = api_cliente.delete(
        f"/api/v1/profissionais/{prof_existente.uuid}/"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Profissional.objects.filter(uuid=prof_existente.uuid).exists()


def test_remocao_de_profissional_inexistente_retorna_404(api_cliente):
    """Testa se a remoção de um profissional inexistente retorna 404."""
    response = api_cliente.delete(
        "/api/v1/profissionais/7ef06bb8-418f-43d1-bfe8-c392f13a2b1f/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remocao_passa_profissional_e_usuario_para_o_servico(
    api_cliente, usuario_ativo
):
    """DELETE delega o profissional e o usuário autenticado ao serviço."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )

    with patch(
        "apps.profissional.api.views.ProfissionalService.deletar"
    ) as deletar:
        response = api_cliente.delete(
            f"/api/v1/profissionais/{profissional.uuid}/"
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    deletar.assert_called_once_with(
        profissional=profissional,
        usuario=usuario_ativo,
    )


def test_remocao_converte_validation_error_do_django(api_cliente):
    """Converte erros da exclusão em resposta de validação da API."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )
    with patch(
        "apps.profissional.api.views.ProfissionalService.deletar",
        side_effect=ValidationError(
            {"profissional": ["Não foi possível excluir o profissional."]}
        ),
    ):
        resposta = api_cliente.delete(
            f"/api/v1/profissionais/{profissional.uuid}/"
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "profissional": ["Não foi possível excluir o profissional."]
    }


def test_atualizacao_converte_erro_de_anexo(api_cliente, cargo_profissional):
    """Converte arquivo inválido na atualização em resposta HTTP 400."""
    profissional = Profissional.objects.create(
        nome="José da Silva",
        cpf="12345678901",
        rg="123456789",
    )
    erro = AnexoArquivoError(
        title="Tipo de arquivo não permitido",
        detail="O tipo de arquivo informado não é permitido.",
    )

    with patch(
        "apps.profissional.api.views.ProfissionalService.atualizar",
        side_effect=erro,
    ):
        resposta = api_cliente.put(
            f"/api/v1/profissionais/{profissional.uuid}/",
            {
                "nome": profissional.nome,
                "cpf": profissional.cpf,
                "rg": profissional.rg,
                "status": profissional.status,
                "funcoes": [
                    {
                        "uuid_cargo": str(cargo_profissional.uuid),
                        "documentos": [],
                    }
                ],
            },
            format="json",
        )

    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert resposta.json() == {
        "title": erro.title,
        "detail": erro.detail,
    }
