"""Testes das views de cargos."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import (
    NotAuthenticated,
    ValidationError as DRFValidationError,
)
from rest_framework.serializers import BaseSerializer

from apps.cargo.api.views import (
    CargoInstabilidadeError,
    CargoViewSet,
)
from apps.cargo.constants import CargoErrorMessages
from apps.cargo.services.cargo_service import CargoService
from apps.usuarios.models.usuario import Usuario


def criar_view(
    service: MagicMock,
    usuario: object | None = None,
) -> CargoViewSet:
    """Cria uma view com suas dependências simuladas.

    Args:
        service: Mock do serviço de cargos.
        usuario: Usuário que será associado à requisição.

    Returns:
        Instância configurada da view de cargos.
    """
    view = CargoViewSet()
    view.service = cast(CargoService, service)
    view.request = cast(
        Any,
        SimpleNamespace(
            user=usuario if usuario is not None else Usuario(),
        ),
    )

    return view


def criar_serializer(
    dados: dict[str, Any],
) -> MagicMock:
    """Cria um serializer simulado com dados validados.

    Args:
        dados: Dados validados que serão atribuídos ao serializer.

    Returns:
        Mock configurado do serializer.
    """
    serializer = MagicMock(spec=BaseSerializer)
    serializer.validated_data = dados
    serializer.instance = None

    return serializer


@patch("apps.cargo.api.views.CargoService")
def test_inicializar_view_com_cargo_service(
    cargo_service_mock: MagicMock,
) -> None:
    """Deve inicializar a view com o serviço de cargos."""
    service = MagicMock()
    cargo_service_mock.return_value = service

    view = CargoViewSet()

    cargo_service_mock.assert_called_once_with()
    assert view.service == service


def test_criar_cargo_delegando_ao_service() -> None:
    """Deve criar um cargo delegando a operação ao service."""
    service = MagicMock()
    usuario = Usuario()
    view = criar_view(service, usuario)
    serializer = criar_serializer(
        {
            "nome": "Eletricista",
            "exige_documento": True,
            "status": True,
            "documentos": [
                {"nome": "Certificado NR-10"},
            ],
        }
    )
    cargo_criado = {
        "pk": 1,
        "nome": "Eletricista",
        "exige_documento": True,
        "status": True,
    }
    service.criar.return_value = cargo_criado

    view.perform_create(serializer)

    service.criar.assert_called_once_with(
        dados=serializer.validated_data,
        usuario=usuario,
    )
    assert serializer.instance == cargo_criado


def test_converter_validacao_com_message_dict_para_erro_drf() -> None:
    """Deve converter uma validação com campos para erro do DRF."""
    service = MagicMock()
    view = criar_view(service)
    serializer = criar_serializer({"nome": ""})

    service.criar.side_effect = DjangoValidationError(
        {
            "nome": ["Este campo não pode ficar em branco."],
        }
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == {
        "nome": ["Este campo não pode ficar em branco."],
    }
    assert serializer.instance is None


def test_converter_validacao_sem_message_dict_para_erro_drf() -> None:
    """Deve converter uma validação sem campos para erro do DRF."""
    service = MagicMock()
    view = criar_view(service)
    serializer = criar_serializer({"nome": "Eletricista"})

    service.criar.side_effect = DjangoValidationError(
        ["Dados inválidos."]
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.detail == ["Dados inválidos."]
    assert serializer.instance is None


def test_retornar_instabilidade_quando_ocorrer_erro_inesperado() -> None:
    """Deve retornar instabilidade quando ocorrer um erro inesperado."""
    service = MagicMock()
    view = criar_view(service)
    serializer = criar_serializer({"nome": "Eletricista"})

    service.criar.side_effect = RuntimeError("Falha inesperada")

    with pytest.raises(CargoInstabilidadeError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == {
        "title": "Erro",
        "detail": CargoErrorMessages.INSTABILIDADE,
    }
    assert serializer.instance is None


def test_obter_usuario_autenticado() -> None:
    """Deve retornar o usuário autenticado da requisição."""
    service = MagicMock()
    usuario = Usuario()
    view = criar_view(service, usuario)

    resultado = view._obter_usuario()

    assert resultado is usuario


def test_rejeitar_usuario_nao_identificado() -> None:
    """Deve rejeitar uma requisição sem usuário identificado."""
    service = MagicMock()
    view = criar_view(
        service,
        usuario=object(),
    )

    with pytest.raises(
        NotAuthenticated,
        match="Usuário não identificado.",
    ):
        view._obter_usuario()
