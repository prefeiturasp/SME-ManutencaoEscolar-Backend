"""Testes do serviço responsável pelas regras de negócio dos lotes."""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from apps.escola.models import DiretoriaRegional
from apps.lote.exceptions import DiretoriaRegionalJaVinculadaError
from apps.lote.models import Lote
from apps.lote.repository.lote_repository import LoteRepository
from apps.lote.services.lote_service import LoteService
from apps.usuarios.models.usuario import Usuario


def test_inicializa_com_repository_padrao() -> None:
    """Deve criar o repository padrão quando nenhum for informado."""
    with patch(
        "apps.lote.services.lote_service.LoteRepository",
        autospec=True,
    ) as repository_class:
        service = LoteService()

    repository_class.assert_called_once_with()
    assert service.repository is repository_class.return_value


def test_inicializa_com_repository_informado() -> None:
    """Deve utilizar o repository recebido na inicialização."""
    repository = Mock(spec=LoteRepository)

    service = LoteService(repository=repository)

    assert service.repository is repository


def test_cria_lote_com_dados_normalizados() -> None:
    """Deve normalizar os dados e encaminhar a criação ao repository."""
    repository = Mock(spec=LoteRepository)
    usuario = Mock(spec=Usuario)
    diretoria = Mock(spec=DiretoriaRegional)

    dados = {
        "codigo_cadastro": "  LOTE-001  ",
        "nome": "  Lote Norte  ",
        "status": True,
        "empresa": 1,
        "periodo_inicial": date(2026, 9, 1),
        "periodo_final": date(2026, 9, 30),
        "diretorias_regionais": [diretoria],
    }

    resultado_esperado = {
        "id": 1,
        "codigo_cadastro": "LOTE-001",
        "nome": "Lote Norte",
    }

    repository._obter_diretorias_regionais_vinculadas.return_value = []
    repository.criar.return_value = resultado_esperado

    service = LoteService(repository=repository)

    resultado = service.criar(dados, usuario)

    repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        [diretoria],
    )

    repository.criar.assert_called_once_with(
        {
            "codigo_cadastro": "LOTE-001",
            "nome": "Lote Norte",
            "status": True,
            "empresa": 1,
            "periodo_inicial": date(2026, 9, 1),
            "periodo_final": date(2026, 9, 30),
            "diretorias_regionais": [diretoria],
        },
        usuario=usuario,
    )

    assert resultado == resultado_esperado

    # O dicionário original não deve ser modificado.
    assert dados["codigo_cadastro"] == "  LOTE-001  "
    assert dados["nome"] == "  Lote Norte  "


def test_rejeita_criacao_com_diretoria_regional_vinculada() -> None:
    """Deve rejeitar a criação quando uma DRE já estiver vinculada."""
    repository = Mock(spec=LoteRepository)
    usuario = Mock(spec=Usuario)
    diretoria = Mock(spec=DiretoriaRegional)

    dados = {
        "codigo_cadastro": "LOTE-001",
        "nome": "Lote Norte",
        "diretorias_regionais": [diretoria],
    }

    vinculados = [
        ("DRE CAPELA DO SOCORRO", "LOTE-002"),
    ]

    repository._obter_diretorias_regionais_vinculadas.return_value = vinculados

    service = LoteService(repository=repository)

    with pytest.raises(DiretoriaRegionalJaVinculadaError):
        service.criar(dados, usuario)

    repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        [diretoria],
    )
    repository.criar.assert_not_called()


def test_atualiza_lote_com_sucesso() -> None:
    """Deve validar as diretorias e encaminhar a atualização."""
    repository = Mock(spec=LoteRepository)
    usuario = Mock(spec=Usuario)
    lote = Mock(spec=Lote)
    diretoria = Mock(spec=DiretoriaRegional)

    dados = {
        "nome": "Lote atualizado",
        "status": True,
        "diretorias_regionais": [diretoria],
    }

    resultado_esperado = {
        "id": 1,
        "nome": "Lote atualizado",
        "status": True,
    }

    repository._obter_diretorias_regionais_vinculadas.return_value = []
    repository.atualizar.return_value = resultado_esperado

    service = LoteService(repository=repository)

    resultado = service.atualizar(
        lote=lote,
        dados=dados,
        usuario=usuario,
    )

    repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        [diretoria],
        lote_ignorado=lote,
    )

    repository.atualizar.assert_called_once_with(
        lote,
        dados,
        usuario=usuario,
    )

    assert resultado == resultado_esperado


def test_rejeita_atualizacao_com_diretoria_regional_vinculada() -> None:
    """Deve rejeitar a atualização quando uma DRE estiver vinculada."""
    repository = Mock(spec=LoteRepository)
    usuario = Mock(spec=Usuario)
    lote = Mock(spec=Lote)
    diretoria = Mock(spec=DiretoriaRegional)

    dados = {
        "nome": "Lote atualizado",
        "diretorias_regionais": [diretoria],
    }

    vinculados = [
        ("DRE CAPELA DO SOCORRO", "LOTE-002"),
    ]

    repository._obter_diretorias_regionais_vinculadas.return_value = vinculados

    service = LoteService(repository=repository)

    with pytest.raises(DiretoriaRegionalJaVinculadaError):
        service.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

    repository._obter_diretorias_regionais_vinculadas.assert_called_once_with(
        [diretoria],
        lote_ignorado=lote,
    )
    repository.atualizar.assert_not_called()
