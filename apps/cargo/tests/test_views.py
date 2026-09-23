"""Testes das views do domínio de cargos."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APIClient

from apps.cargo.api.views import CargoViewSet
from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import CargoInstabilidadeError
from apps.cargo.filters import CargoFilter
from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.serializers import CargoCriarSerializer, CargoSerializer
from apps.cargo.services.cargo_service import CargoService
from apps.core.pagination import PaginacaoPadrao
from apps.usuarios.models.usuario import Usuario

pytestmark = pytest.mark.django_db

CARGOS_URL = "/api/v1/cargos/"
UUID_INEXISTENTE = "7ef06bb8-418f-43d1-bfe8-c392f13a2b1f"


def test_inicializar_view_com_service_padrao() -> None:
    """Deve inicializar a view com o serviço padrão."""
    view = CargoViewSet()

    assert isinstance(view.service, CargoService)


def test_configurar_view() -> None:
    """Deve configurar métodos, filtros, paginação e campo de busca."""
    view = CargoViewSet()

    assert view.http_method_names == [
        "get",
        "post",
        "patch",
        "options",
        "delete",
    ]
    assert view.lookup_field == "uuid"
    assert view.filter_backends == [DjangoFilterBackend]
    assert view.filterset_class is CargoFilter
    assert view.pagination_class is PaginacaoPadrao


@pytest.mark.parametrize(
    "acao",
    [
        "create",
        "partial_update",
    ],
)
def test_get_serializer_class_deve_usar_serializer_de_escrita(
    acao: str,
) -> None:
    """Deve utilizar o serializer de escrita nas alterações."""
    view = CargoViewSet()
    view.action = acao

    resultado = view.get_serializer_class()

    assert resultado is CargoCriarSerializer


@pytest.mark.parametrize(
    "acao",
    [
        "list",
        "retrieve",
        "destroy",
    ],
)
def test_get_serializer_class_deve_usar_serializer_de_leitura(
    acao: str,
) -> None:
    """Deve utilizar o serializer de leitura nas demais ações."""
    view = CargoViewSet()
    view.action = acao

    resultado = view.get_serializer_class()

    assert resultado is CargoSerializer


def test_obter_usuario_deve_retornar_usuario_autenticado(
    usuario_ativo: Usuario,
) -> None:
    """Deve retornar o usuário autenticado da requisição."""
    view = CargoViewSet()

    cast(Any, view).request = SimpleNamespace(
        user=usuario_ativo,
    )

    resultado = view._obter_usuario()

    assert resultado is usuario_ativo


def test_obter_usuario_deve_rejeitar_usuario_invalido() -> None:
    """Deve rejeitar uma requisição sem usuário autenticado."""
    view = CargoViewSet()

    cast(Any, view).request = SimpleNamespace(
        user=AnonymousUser(),
    )

    with pytest.raises(
        NotAuthenticated,
        match="Usuário não identificado.",
    ):
        view._obter_usuario()


def test_obter_cargo_deve_retornar_instancia_do_serializer(
    cargo: Cargo,
) -> None:
    """Deve retornar o cargo presente no serializer."""
    serializer = CargoCriarSerializer(
        instance=cargo,
    )

    resultado = CargoViewSet._obter_cargo(serializer)

    assert resultado is cargo


def test_obter_cargo_deve_rejeitar_instancia_ausente() -> None:
    """Deve rejeitar serializer sem instância."""
    serializer = CargoCriarSerializer()

    with pytest.raises(DRFValidationError) as exc_info:
        CargoViewSet._obter_cargo(serializer)

    assert exc_info.value.detail == {
        "title": "Erro",
        "detail": "Cargo inválido ou não encontrado.",
    }


def test_obter_cargo_deve_rejeitar_instancia_de_outro_tipo() -> None:
    """Deve rejeitar uma instância que não seja um cargo."""
    serializer = CargoCriarSerializer()
    cast(Any, serializer).instance = object()

    with pytest.raises(DRFValidationError) as exc_info:
        CargoViewSet._obter_cargo(serializer)

    assert exc_info.value.detail == {
        "title": "Erro",
        "detail": "Cargo inválido ou não encontrado.",
    }


def test_requisicao_nao_autenticada_retorna_401(
    cargo_payload_valido,
) -> None:
    """Deve rejeitar a criação sem autenticação."""
    response = APIClient().post(
        CARGOS_URL,
        cargo_payload_valido,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_criacao_retorna_cargo(
    api_cliente,
    cargo_payload_valido,
    usuario_ativo: Usuario,
) -> None:
    """Deve criar e retornar um cargo pela API."""
    response = api_cliente.post(
        CARGOS_URL,
        cargo_payload_valido,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    dados = response.json()
    cargo = Cargo.objects.get(
        nome=cargo_payload_valido["nome"],
    )
    documentos = DocumentoCargo.objects.filter(
        cargo=cargo,
    )

    assert dados["nome"] == cargo_payload_valido["nome"]
    assert dados["exige_documento"] is True
    assert dados["status"] is True

    assert cargo.nome == cargo_payload_valido["nome"]
    assert cargo.criado_por == usuario_ativo
    assert cargo.atualizado_por == usuario_ativo
    assert documentos.count() == 2


def test_criacao_rejeita_cargo_com_nome_duplicado(
    api_cliente,
    cargo: Cargo,
    cargo_payload_valido_sem_documentos,
) -> None:
    """Deve retornar 400 quando o nome do cargo já existir."""
    payload = {
        **cargo_payload_valido_sem_documentos,
        "nome": cargo.nome,
    }

    response = api_cliente.post(
        CARGOS_URL,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "title": CargoErrorMessages.CARGO_VINCULADO_TITULO,
        "detail": {
            "message": (
                CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                    nome=cargo.nome,
                )
            ),
        },
    }


def test_criacao_rejeita_documentos_duplicados(
    api_cliente,
    cargo_payload_valido,
) -> None:
    """Deve retornar 400 quando existem documentos duplicados."""
    payload = {
        **cargo_payload_valido,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
            {
                "nome": "CERTIFICADO NR-10",
            },
        ],
    }

    response = api_cliente.post(
        CARGOS_URL,
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "title": CargoErrorMessages.DOCUMENTO_VINCULADO_TITULO,
        "detail": {
            "message": (
                CargoErrorMessages.DOCUMENTO_VINCULADO_CORPO.format(
                    nome_documento="CERTIFICADO NR-10",
                    nome_cargo=cargo_payload_valido["nome"],
                )
            ),
        },
    }


def test_criacao_mapeia_validation_error_com_dicionario(
    api_cliente,
    cargo_payload_valido,
) -> None:
    """Deve converter ValidationError com dicionário em resposta 400."""
    with patch(
        "apps.cargo.api.views.CargoService.criar",
        side_effect=DjangoValidationError(
            {
                "nome": [
                    "Já existe um cargo com este nome.",
                ],
            },
        ),
    ):
        response = api_cliente.post(
            CARGOS_URL,
            cargo_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "nome": [
            "Já existe um cargo com este nome.",
        ],
    }


def test_criacao_mapeia_validation_error_com_lista(
    api_cliente,
    cargo_payload_valido,
) -> None:
    """Deve converter ValidationError com lista em resposta 400."""
    with patch(
        "apps.cargo.api.views.CargoService.criar",
        side_effect=DjangoValidationError(
            [
                "Dados inválidos.",
            ],
        ),
    ):
        response = api_cliente.post(
            CARGOS_URL,
            cargo_payload_valido,
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [
        "Dados inválidos.",
    ]


def test_criacao_mapeia_erro_inesperado(
    api_cliente,
    cargo_payload_valido,
) -> None:
    """Deve converter erro inesperado em erro de instabilidade."""
    with patch(
        "apps.cargo.api.views.CargoService.criar",
        side_effect=RuntimeError("Falha inesperada."),
    ):
        response = api_cliente.post(
            CARGOS_URL,
            cargo_payload_valido,
            format="json",
        )

    assert response.status_code == CargoInstabilidadeError.status_code
    assert response.json() == {
        "title": "Erro",
        "detail": CargoErrorMessages.INSTABILIDADE,
    }


def test_listagem_retorna_cargos(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve retornar os cargos cadastrados."""
    response = api_cliente.get(CARGOS_URL)

    assert response.status_code == status.HTTP_200_OK

    dados = response.json()

    assert dados["count"] == 1
    assert len(dados["results"]) == 1
    assert dados["results"][0]["uuid"] == str(cargo.uuid)
    assert dados["results"][0]["nome"] == cargo.nome


def test_recuperacao_retorna_cargo_por_uuid(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve recuperar um cargo pelo UUID."""
    response = api_cliente.get(
        f"{CARGOS_URL}{cargo.uuid}/",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["uuid"] == str(cargo.uuid)
    assert response.json()["nome"] == cargo.nome


def test_recuperacao_de_cargo_inexistente_retorna_404(
    api_cliente,
) -> None:
    """Deve retornar 404 quando o cargo não existir."""
    response = api_cliente.get(
        f"{CARGOS_URL}{UUID_INEXISTENTE}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_atualizacao_retorna_cargo(
    api_cliente,
    cargo: Cargo,
    cargo_payload_atualizacao_valido,
    usuario_ativo: Usuario,
) -> None:
    """Deve atualizar e retornar o cargo pela API."""
    response = api_cliente.patch(
        f"{CARGOS_URL}{cargo.uuid}/",
        cargo_payload_atualizacao_valido,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cargo.refresh_from_db()
    dados = response.json()

    assert cargo.nome == cargo_payload_atualizacao_valido["nome"]
    assert cargo.exige_documento is True
    assert cargo.status is False
    assert cargo.atualizado_por == usuario_ativo
    assert dados["nome"] == cargo_payload_atualizacao_valido["nome"]


def test_atualizacao_rejeita_nome_de_outro_cargo(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve retornar 400 quando outro cargo possui o nome informado."""
    Cargo.objects.create(
        nome="Encanador",
        exige_documento=False,
        status=True,
    )

    response = api_cliente.patch(
        f"{CARGOS_URL}{cargo.uuid}/",
        {
            "nome": "Encanador",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "title": CargoErrorMessages.CARGO_VINCULADO_TITULO,
        "detail": {
            "message": (
                CargoErrorMessages.CARGO_VINCULADO_CORPO.format(
                    nome="Encanador",
                )
            ),
        },
    }

    cargo.refresh_from_db()

    assert cargo.nome == "Eletricista"


def test_atualizacao_rejeita_documentos_duplicados(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve retornar 400 quando existem documentos duplicados."""
    response = api_cliente.patch(
        f"{CARGOS_URL}{cargo.uuid}/",
        {
            "documentos": [
                {
                    "nome": "Certificado NR-10",
                },
                {
                    "nome": "CERTIFICADO NR-10",
                },
            ],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    erros = response.json()

    assert "documentos" in erros
    assert len(erros["documentos"]) == 1
    assert "vinculados" in erros["documentos"][0].lower()


def test_atualizacao_mapeia_validation_error_com_dicionario(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve converter ValidationError com dicionário em resposta 400."""
    with patch(
        "apps.cargo.api.views.CargoService.atualizar",
        side_effect=DjangoValidationError(
            {
                "nome": [
                    "Já existe um cargo com este nome.",
                ],
            },
        ),
    ):
        response = api_cliente.patch(
            f"{CARGOS_URL}{cargo.uuid}/",
            {
                "status": False,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "nome": [
            "Já existe um cargo com este nome.",
        ],
    }


def test_atualizacao_mapeia_validation_error_com_lista(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve converter ValidationError com lista em resposta 400."""
    with patch(
        "apps.cargo.api.views.CargoService.atualizar",
        side_effect=DjangoValidationError(
            [
                "Dados inválidos.",
            ],
        ),
    ):
        response = api_cliente.patch(
            f"{CARGOS_URL}{cargo.uuid}/",
            {
                "status": False,
            },
            format="json",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [
        "Dados inválidos.",
    ]


def test_atualizacao_mapeia_erro_inesperado(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve converter erro inesperado em erro de instabilidade."""
    with patch(
        "apps.cargo.api.views.CargoService.atualizar",
        side_effect=RuntimeError(
            "Falha inesperada durante a atualização.",
        ),
    ):
        response = api_cliente.patch(
            f"{CARGOS_URL}{cargo.uuid}/",
            {
                "status": False,
            },
            format="json",
        )

    assert response.status_code == CargoInstabilidadeError.status_code
    assert response.json() == {
        "title": "Erro",
        "detail": CargoErrorMessages.INSTABILIDADE,
    }


def test_atualizacao_sem_autenticacao_retorna_401(
    cargo: Cargo,
) -> None:
    """Deve rejeitar a atualização sem autenticação."""
    response = APIClient().patch(
        f"{CARGOS_URL}{cargo.uuid}/",
        {
            "status": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    cargo.refresh_from_db()

    assert cargo.status is True


def test_atualizacao_de_cargo_inexistente_retorna_404(
    api_cliente,
) -> None:
    """Deve retornar 404 quando o cargo não existir."""
    response = api_cliente.patch(
        f"{CARGOS_URL}{UUID_INEXISTENTE}/",
        {
            "status": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remocao_deleta_cargo_e_some_da_listagem(
    api_cliente,
    cargo: Cargo,
) -> None:
    """Deve excluir logicamente o cargo pela API."""
    response = api_cliente.delete(
        f"{CARGOS_URL}{cargo.uuid}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Cargo.objects.filter(
        uuid=cargo.uuid,
    ).exists()


def test_remocao_de_cargo_inexistente_retorna_404(
    api_cliente,
) -> None:
    """Deve retornar 404 quando o cargo não existir."""
    response = api_cliente.delete(
        f"{CARGOS_URL}{UUID_INEXISTENTE}/",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remocao_sem_autenticacao_retorna_401(
    cargo: Cargo,
) -> None:
    """Deve rejeitar a exclusão sem autenticação."""
    response = APIClient().delete(
        f"{CARGOS_URL}{cargo.uuid}/",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Cargo.objects.filter(
        uuid=cargo.uuid,
    ).exists()
