# Create your tests here.
"""Testes das views relacionadas aos lotes."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
)
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer

from apps.lote.api.views import (
    LoteInstabilidadeError,
    LoteViewSet,
)
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import (
    DiretoriaRegionalJaVinculadaError,
)
from apps.lote.models import Lote
from apps.lote.serializers import (
    LoteCriarSerializer,
    LoteSerializer,
)
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


def criar_view(
    usuario: object,
) -> tuple[LoteViewSet, Mock]:
    """Cria uma view com usuário e serviço simulados."""
    view = LoteViewSet()
    view.request = cast(
        Request,
        SimpleNamespace(user=usuario),
    )
    service_mock = Mock(spec=LoteService)
    view.service = cast(
        LoteService,
        service_mock,
    )

    return view, service_mock


def criar_serializer_mock(
    dados: dict[str, Any],
) -> tuple[BaseSerializer, Mock]:
    """Cria um serializer simulado com dados validados."""
    serializer_mock = Mock(spec=BaseSerializer)
    serializer_mock.validated_data = dados
    serializer_mock.instance = None

    return (
        cast(BaseSerializer, serializer_mock),
        serializer_mock,
    )


def test_inicializa_view_com_service_padrao() -> None:
    """Deve inicializar a view com o serviço de lotes."""
    with patch(
        "apps.lote.api.views.LoteService",
    ) as service_class:
        service = service_class.return_value

        view = LoteViewSet()

    assert view.service is service
    service_class.assert_called_once_with()


def test_retorna_usuario_autenticado() -> None:
    """Deve retornar o usuário autenticado na requisição."""
    usuario = Usuario()
    view, _ = criar_view(usuario)

    resultado = view._obter_usuario()

    assert resultado is usuario


def test_rejeita_usuario_nao_identificado() -> None:
    """Deve rejeitar usuário que não seja uma instância válida."""
    view, _ = criar_view(object())

    with pytest.raises(NotAuthenticated) as exc_info:
        view._obter_usuario()

    assert str(exc_info.value.detail) == ("Usuário não identificado.")


def test_retorna_serializer_de_criacao() -> None:
    """Deve retornar o serializer de criação na ação create."""
    view = LoteViewSet()
    view.action = "create"

    resultado = view.get_serializer_class()

    assert resultado is LoteCriarSerializer


def test_retorna_serializer_de_leitura() -> None:
    """Deve retornar o serializer de leitura em outra ação."""
    view = LoteViewSet()
    view.action = "retrieve"

    resultado = view.get_serializer_class()

    assert resultado is LoteSerializer


def test_realiza_criacao_do_lote() -> None:
    """Deve criar o lote utilizando os dados validados."""
    usuario = Usuario()
    view, service_mock = criar_view(usuario)
    dados: dict[str, Any] = {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
    }
    serializer, serializer_mock = criar_serializer_mock(dados)
    lote_criado: dict[str, Any] = {
        "id": 1,
        "nome": "Lote Centro",
    }
    service_mock.criar.return_value = lote_criado

    view.perform_create(serializer)

    service_mock.criar.assert_called_once_with(
        dados=dados,
        usuario=usuario,
    )
    assert serializer_mock.instance == lote_criado


def test_converte_erro_de_diretoria_em_erro_de_validacao() -> None:
    """Deve converter conflito de DRE em erro de validação."""
    usuario = Usuario()
    view, service_mock = criar_view(usuario)
    serializer, serializer_mock = criar_serializer_mock({})
    erro = DiretoriaRegionalJaVinculadaError(
        title="Diretoria Regional já vinculada",
        detail={
            "message": (LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA),
            "vinculados": [
                (
                    "Diretoria Regional Centro",
                    "LOTE-002",
                )
            ],
        },
    )
    service_mock.criar.side_effect = erro

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert str(exc_info.value.detail["title"]) == erro.title
    assert "detail" in exc_info.value.detail
    assert serializer_mock.instance is None


def test_converte_validation_error_com_message_dict() -> None:
    """Deve converter erros de validação organizados por campo."""
    usuario = Usuario()
    view, service_mock = criar_view(usuario)
    serializer, _ = criar_serializer_mock({})
    service_mock.criar.side_effect = ValidationError(
        {
            "nome": [
                "Este campo é obrigatório.",
            ]
        }
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert str(exc_info.value.detail["nome"][0]) == (
        "Este campo é obrigatório."
    )


def test_converte_validation_error_com_messages() -> None:
    """Deve converter erros de validação sem campo específico."""
    usuario = Usuario()
    view, service_mock = criar_view(usuario)
    serializer, _ = criar_serializer_mock({})
    service_mock.criar.side_effect = ValidationError(
        "Dados inválidos.",
    )

    with pytest.raises(DRFValidationError) as exc_info:
        view.perform_create(serializer)

    assert str(exc_info.value.detail[0]) == "Dados inválidos."


def test_converte_erro_inesperado_em_instabilidade() -> None:
    """Deve converter erros inesperados em instabilidade."""
    usuario = Usuario()
    view, service_mock = criar_view(usuario)
    serializer, _ = criar_serializer_mock({})
    service_mock.criar.side_effect = RuntimeError(
        "Erro inesperado.",
    )

    with pytest.raises(LoteInstabilidadeError) as exc_info:
        view.perform_create(serializer)

    assert exc_info.value.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    assert str(exc_info.value.detail["title"]) == "Erro"
    assert str(exc_info.value.detail["detail"]) == (
        LoteErrorMessages.INSTABILIDADE
    )


def test_configuracao_do_erro_de_instabilidade() -> None:
    """Deve configurar corretamente o erro de instabilidade."""
    erro = LoteInstabilidadeError()

    assert erro.status_code == (status.HTTP_500_INTERNAL_SERVER_ERROR)
    assert str(erro.detail) == LoteErrorMessages.INSTABILIDADE
    assert erro.default_code == "lote_instabilidade"


def test_obtem_lote_do_serializer() -> None:
    """Deve retornar o lote presente na instância do serializer."""
    lote = Lote(
        nome="Lote Centro",
        codigo_cadastro="LOTE-001",
    )
    serializer, serializer_mock = criar_serializer_mock({})
    serializer_mock.instance = lote

    resultado = LoteViewSet._obter_lote(serializer)

    assert resultado is lote


def test_rejeita_serializer_sem_instancia_de_lote() -> None:
    """Deve rejeitar serializer que não possua um lote válido."""
    serializer, _ = criar_serializer_mock({})

    with pytest.raises(DRFValidationError) as exc_info:
        LoteViewSet._obter_lote(serializer)

    assert str(exc_info.value.detail["title"]) == "Erro"
    assert str(exc_info.value.detail["detail"]) == (
        "Serviço inválido ou não encontrado."
    )
