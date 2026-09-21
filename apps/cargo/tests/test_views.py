"""Testes das views do domínio de cargos."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.cargo.api.views import CargoViewSet
from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import (
    CargoInstabilidadeError,
    CargoOuDocumentoJaVinculadaError,
)
from apps.cargo.filters import CargoFilter
from apps.cargo.models import Cargo, DocumentoCargo
from apps.cargo.serializers import (
    CargoCriarSerializer,
    CargoListagemSerializer,
    CargoSerializer,
)
from apps.core.pagination import PaginacaoPadrao
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def usuario() -> Usuario:
    """Retorna um usuário para os testes.

    Returns:
        Usuário utilizado na requisição.
    """
    return Usuario()


@pytest.fixture
def view(usuario: Usuario) -> CargoViewSet:
    """Retorna a view configurada com usuário e service simulados.

    Args:
        usuario: Usuário autenticado da requisição.

    Returns:
        View de cargos configurada para os testes.
    """
    cargo_view = CargoViewSet()

    cast(Any, cargo_view).request = SimpleNamespace(
        user=usuario,
    )
    cargo_view.service = MagicMock()

    return cargo_view


@pytest.fixture
def serializer() -> MagicMock:
    """Retorna um serializer simulado.

    Returns:
        Serializer contendo dados validados de cargo.
    """
    serializer_mock = MagicMock()
    serializer_mock.validated_data = {
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }
    serializer_mock.instance = None

    return serializer_mock


@patch("apps.cargo.api.views.CargoService")
def test_inicializar_view_com_service_padrao(
    cargo_service_mock: MagicMock,
) -> None:
    """Deve inicializar a view com o service padrão."""
    service = MagicMock()
    cargo_service_mock.return_value = service

    view = CargoViewSet()

    cargo_service_mock.assert_called_once_with()
    assert view.service is service


def test_perform_create_deve_criar_cargo(
    view: CargoViewSet,
    serializer: MagicMock,
    usuario: Usuario,
) -> None:
    """Deve criar o cargo usando o service."""
    cargo_criado = {
        "pk": 1,
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "Certificado NR-10",
            },
        ],
    }
    view.service.criar.return_value = cargo_criado

    view.perform_create(serializer)

    view.service.criar.assert_called_once_with(
        dados=serializer.validated_data,
        usuario=usuario,
    )
    assert serializer.instance == cargo_criado


def test_perform_create_deve_tratar_cargo_ou_documento_duplicado(
    view: CargoViewSet,
    serializer: MagicMock,
) -> None:
    """Deve converter o erro de duplicidade em erro de validação DRF."""
    erro_original = CargoOuDocumentoJaVinculadaError(
        title="Cargo já cadastrado",
        detail={
            "message": (
                "Já existe um cargo com o nome Eletricista cadastrado."
            ),
        },
    )
    view.service.criar.side_effect = erro_original

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == {
        "title": "Cargo já cadastrado",
        "detail": {
            "message": (
                "Já existe um cargo com o nome Eletricista cadastrado."
            ),
        },
    }
    assert exc_info.value.__cause__ is erro_original
    assert serializer.instance is None


def test_perform_create_deve_tratar_validation_error_com_dicionario(
    view: CargoViewSet,
    serializer: MagicMock,
) -> None:
    """Deve converter ValidationError com dicionário para erro DRF."""
    erro_original = DjangoValidationError(
        {
            "nome": [
                "Já existe um cargo com este nome.",
            ],
        },
    )
    view.service.criar.side_effect = erro_original

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == {
        "nome": [
            "Já existe um cargo com este nome.",
        ],
    }
    assert exc_info.value.__cause__ is erro_original
    assert serializer.instance is None


def test_perform_create_deve_tratar_validation_error_com_lista(
    view: CargoViewSet,
    serializer: MagicMock,
) -> None:
    """Deve converter ValidationError com lista para erro DRF."""
    erro_original = DjangoValidationError(
        [
            "Dados inválidos.",
        ],
    )
    view.service.criar.side_effect = erro_original

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == [
        "Dados inválidos.",
    ]
    assert exc_info.value.__cause__ is erro_original
    assert serializer.instance is None


def test_perform_create_deve_tratar_erro_inesperado(
    view: CargoViewSet,
    serializer: MagicMock,
) -> None:
    """Deve converter um erro inesperado em erro de instabilidade."""
    erro_original = RuntimeError("Falha inesperada")
    view.service.criar.side_effect = erro_original

    with pytest.raises(CargoInstabilidadeError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == {
        "title": "Erro",
        "detail": CargoErrorMessages.INSTABILIDADE,
    }
    assert exc_info.value.__cause__ is erro_original
    assert serializer.instance is None


def test_obter_usuario_deve_retornar_usuario_autenticado(
    view: CargoViewSet,
    usuario: Usuario,
) -> None:
    """Deve retornar o usuário autenticado da requisição."""
    resultado = view._obter_usuario()

    assert resultado is usuario


def test_obter_usuario_deve_rejeitar_usuario_invalido() -> None:
    """Deve rejeitar uma requisição sem um usuário válido."""
    view = CargoViewSet()

    cast(Any, view).request = SimpleNamespace(
        user=MagicMock(),
    )

    with pytest.raises(
        NotAuthenticated,
        match="Usuário não identificado.",
    ):
        view._obter_usuario()


def test_configurar_metodos_http_permitidos() -> None:
    """Deve permitir somente POST, GET e  OPTIONS."""
    view = CargoViewSet()

    assert view.http_method_names == [
        "get",
        "post",
        "options",
    ]
    assert view.lookup_field == "uuid"
    assert view.filter_backends == [DjangoFilterBackend]
    assert view.filterset_class is CargoFilter
    assert view.pagination_class is PaginacaoPadrao


@pytest.mark.parametrize("acao", ["create", "partial_update"])
def test_get_serializer_class_deve_usar_serializer_de_criacao(
    view: CargoViewSet,
    acao: str,
) -> None:
    """Usa o serializer de escrita nas ações de criação e edição parcial."""
    view.action = acao

    resultado = view.get_serializer_class()

    assert resultado is CargoCriarSerializer


def test_get_serializer_class_deve_usar_serializer_de_leitura(
    view: CargoViewSet,
) -> None:
    """Usa o serializer de leitura na consulta de um cargo."""
    view.action = "retrieve"

    resultado = view.get_serializer_class()

    assert resultado is CargoSerializer


def test_get_serializer_class_deve_usar_serializer_de_listagem(
    view: CargoViewSet,
) -> None:
    """Usa o serializer resumido na listagem de cargos."""
    view.action = "list"

    assert view.get_serializer_class() is CargoListagemSerializer


@pytest.mark.django_db
def test_listar_todos_os_cargos_com_page_size_all(api_cliente: Any) -> None:
    """Deve listar todos os cargos com os campos resumidos e metadados."""
    cargo = Cargo.objects.create(nome="Eletricista", exige_documento=True)
    DocumentoCargo.objects.create(
        cargo=cargo,
        nome="Certificado NR-10",
    )
    cargo_sem_documento = Cargo.objects.create(
        nome="Auxiliar",
        exige_documento=False,
    )

    resposta = api_cliente.get("/api/v1/cargos/?page_size=all")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "uuid": str(cargo_sem_documento.uuid),
                "nome": "Auxiliar",
                "exige_documento": False,
                "documentos": [],
            },
            {
                "uuid": str(cargo.uuid),
                "nome": "Eletricista",
                "exige_documento": True,
                "documentos": [{"nome": "Certificado NR-10"}],
            },
        ],
    }
