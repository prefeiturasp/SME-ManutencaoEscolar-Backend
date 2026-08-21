"""Testes dos serviços relacionados aos lotes."""

from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from apps.escola.models import DiretoriaRegional
from apps.lote.constants import LoteErrorMessages
from apps.lote.exceptions import (
    DiretoriaRegionalJaVinculadaError,
)
from apps.lote.repository.lote_repository import LoteRepository
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


def criar_repository_mock() -> tuple[LoteRepository, Mock]:
    """Cria um repositório simulado para os testes."""
    repository_mock = Mock(spec=LoteRepository)

    return (
        cast(LoteRepository, repository_mock),
        repository_mock,
    )


def criar_usuario_mock() -> Usuario:
    """Cria um usuário simulado para os testes."""
    return cast(Usuario, Mock(spec=Usuario))


def test_inicializa_com_repository_padrao() -> None:
    """Deve inicializar o serviço com o repositório padrão."""
    with patch(
        "apps.lote.services.lote_service.LoteRepository",
    ) as repository_class:
        repository = repository_class.return_value

        service = LoteService()

    assert service.repository is repository
    repository_class.assert_called_once_with()


def test_inicializa_com_repository_informado() -> None:
    """Deve utilizar o repositório recebido na inicialização."""
    repository, _ = criar_repository_mock()

    service = LoteService(repository=repository)

    assert service.repository is repository


def test_cria_lote_com_dados_normalizados() -> None:
    """Deve remover espaços do nome e do código antes da criação."""
    repository, repository_mock = criar_repository_mock()
    usuario = criar_usuario_mock()
    diretoria_regional = DiretoriaRegional(pk=1)
    dados: dict[str, Any] = {
        "nome": "  Lote Centro  ",
        "codigo_cadastro": "  LOTE-001  ",
        "diretorias_regionais": [diretoria_regional],
        "status": True,
    }
    resultado_esperado: dict[str, Any] = {
        "id": 1,
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
    }
    repository_mock._obter_diretorias_regionais_vinculadas.return_value = []
    repository_mock.criar.return_value = resultado_esperado
    service = LoteService(repository=repository)

    resultado = service.criar(
        dados=dados,
        usuario=usuario,
    )

    assert resultado == resultado_esperado
    repository_mock._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        [diretoria_regional]
    )
    repository_mock.criar.assert_called_once_with(
        {
            "nome": "Lote Centro",
            "codigo_cadastro": "LOTE-001",
            "diretorias_regionais": [diretoria_regional],
            "status": True,
        },
        usuario=usuario,
    )


def test_nao_altera_dicionario_original() -> None:
    """Deve preservar os dados originais recebidos pelo serviço."""
    repository, repository_mock = criar_repository_mock()
    usuario = criar_usuario_mock()
    dados: dict[str, Any] = {
        "nome": "  Lote Centro  ",
        "codigo_cadastro": "  LOTE-001  ",
    }
    dados_originais = dados.copy()
    repository_mock._obter_diretorias_regionais_vinculadas.return_value = []
    repository_mock.criar.return_value = {}
    service = LoteService(repository=repository)

    service.criar(
        dados=dados,
        usuario=usuario,
    )

    assert dados == dados_originais


def test_consulta_lista_vazia_quando_nao_recebe_diretorias() -> None:
    """Deve consultar vínculos com lista vazia quando não houver DREs."""
    repository, repository_mock = criar_repository_mock()
    usuario = criar_usuario_mock()
    dados: dict[str, Any] = {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
    }
    repository_mock._obter_diretorias_regionais_vinculadas.return_value = []
    repository_mock.criar.return_value = {}
    service = LoteService(repository=repository)

    service.criar(
        dados=dados,
        usuario=usuario,
    )

    repository_mock._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        []
    )


def test_rejeita_diretoria_regional_ja_vinculada() -> None:
    """Deve rejeitar uma Diretoria Regional vinculada a outro lote."""
    repository, repository_mock = criar_repository_mock()
    usuario = criar_usuario_mock()
    diretoria_regional = DiretoriaRegional(pk=1)
    dados: dict[str, Any] = {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
        "diretorias_regionais": [diretoria_regional],
    }
    vinculados = [
        (
            "Diretoria Regional Centro",
            "LOTE-002",
        )
    ]
    repository_mock._obter_diretorias_regionais_vinculadas.return_value = (
        vinculados
    )
    service = LoteService(repository=repository)

    with pytest.raises(
        DiretoriaRegionalJaVinculadaError,
    ) as exc_info:
        service.criar(
            dados=dados,
            usuario=usuario,
        )

    assert str(exc_info.value.detail["message"]) == (
        LoteErrorMessages.DIRETORIA_REGIONAL_VINCULADA
    )
    repository_mock.criar.assert_not_called()
