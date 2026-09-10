"""Testes das views do domínio de cargos."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.cargo.api.views import CargoViewSet
from apps.cargo.constants import CargoErrorMessages
from apps.cargo.exceptions import CargoInstabilidadeError
from apps.cargo.models import Cargo
from apps.usuarios.models.usuario import Usuario


@pytest.fixture
def usuario() -> Usuario:
    """Retorna um usuário para os testes da view."""
    return Usuario()


@pytest.fixture
def view(usuario: Usuario) -> CargoViewSet:
    """Retorna a view configurada com usuário e service mockado."""
    cargo_view = CargoViewSet()
    cargo_view.request = SimpleNamespace(user=usuario)
    cargo_view.service = Mock()

    return cargo_view


@pytest.fixture
def serializer() -> Mock:
    """Retorna um serializer mockado com dados validados."""
    serializer_mock = Mock()
    serializer_mock.validated_data = {
        "nome": "Encanador",
        "exige_documento": True,
        "status": True,
        "documentos": [
            {
                "nome": "NR10",
            },
        ],
    }
    serializer_mock.instance = None

    return serializer_mock


def test_inicializar_view_com_cargo_service() -> None:
    """Testa a inicialização da view com o service de cargos."""
    service_mock = Mock()

    with patch(
        "apps.cargo.api.views.CargoService",
        return_value=service_mock,
    ) as cargo_service_mock:
        cargo_view = CargoViewSet()

    cargo_service_mock.assert_called_once_with()
    assert cargo_view.service is service_mock


def test_perform_create_deve_criar_cargo(
    view: CargoViewSet,
    serializer: Mock,
    usuario: Usuario,
) -> None:
    """Testa a criação de um cargo por meio do service."""
    cargo_criado = Cargo(
        nome="Encanador",
        exige_documento=True,
        status=True,
    )
    view.service.criar.return_value = cargo_criado

    view.perform_create(serializer)

    view.service.criar.assert_called_once_with(
        dados=serializer.validated_data,
        usuario=usuario,
    )
    assert serializer.instance is cargo_criado


def test_perform_create_deve_converter_validation_error_com_dicionario(
    view: CargoViewSet,
    serializer: Mock,
) -> None:
    """Testa a conversão de ValidationError contendo message_dict."""
    view.service.criar.side_effect = DjangoValidationError(
        {
            "nome": [
                "Já existe um cargo com este nome.",
            ],
        },
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == {
        "nome": [
            "Já existe um cargo com este nome.",
        ],
    }
    assert serializer.instance is None


def test_perform_create_deve_converter_validation_error_com_lista(
    view: CargoViewSet,
    serializer: Mock,
) -> None:
    """Testa a conversão de ValidationError contendo uma lista."""
    view.service.criar.side_effect = DjangoValidationError(
        [
            "Dados do cargo inválidos.",
        ],
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == [
        "Dados do cargo inválidos.",
    ]
    assert serializer.instance is None


def test_perform_create_deve_lancar_erro_de_instabilidade(
    view: CargoViewSet,
    serializer: Mock,
) -> None:
    """Testa o tratamento de uma falha inesperada do service."""
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
    """Testa o retorno do usuário autenticado."""
    resultado = view._obter_usuario()

    assert resultado is usuario


def test_obter_usuario_deve_lancar_not_authenticated() -> None:
    """Testa a ausência de um usuário válido na requisição."""
    cargo_view = CargoViewSet()
    cargo_view.request = SimpleNamespace(user=Mock())

    with pytest.raises(
        NotAuthenticated,
        match="Usuário não identificado.",
    ):
        cargo_view._obter_usuario()


def test_view_deve_permitir_somente_post_e_options() -> None:
    """Testa os métodos HTTP permitidos pela view."""
    assert CargoViewSet.http_method_names == [
        "post",
        "options",
    ]
