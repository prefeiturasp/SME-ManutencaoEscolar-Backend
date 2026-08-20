"""Testes do repositório de lotes."""

from typing import Any, cast
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote, LoteDiretoriaRegional
from apps.lote.repository.lote_repository import LoteRepository
from apps.usuarios.models.usuario import Usuario


def criar_usuario_mock() -> Usuario:
    """Cria um usuário simulado para os testes."""
    return cast(Usuario, Mock(spec=Usuario))


def test_obtem_diretorias_regionais_vinculadas() -> None:
    """Deve retornar os nomes das DREs e dos lotes vinculados."""
    repository = LoteRepository()
    vinculo_model_mock = Mock()
    repository.vinculo_model = cast(
        type[LoteDiretoriaRegional],
        vinculo_model_mock,
    )
    diretorias_regionais = [
        DiretoriaRegional(pk=1),
        DiretoriaRegional(pk=2),
    ]
    vinculos = [
        (
            "Diretoria Regional Centro",
            "LOTE-001",
        ),
        (
            "Diretoria Regional Norte",
            "LOTE-002",
        ),
    ]
    filtro_mock = vinculo_model_mock.objects.filter.return_value
    filtro_mock.values_list.return_value = vinculos

    resultado = repository._obter_diretorias_regionais_vinculadas(
        diretorias_regionais,
    )

    assert resultado == vinculos
    vinculo_model_mock.objects.filter.assert_called_once_with(
        diretoria_regional_id__in=[1, 2],
    )
    filtro_mock.values_list.assert_called_once_with(
        "diretoria_regional__nome",
        "lote__codigo_cadastro",
    )


def test_converte_dados_dos_vinculos_para_string() -> None:
    """Deve converter os dados dos vínculos para strings."""
    repository = LoteRepository()
    vinculo_model_mock = Mock()
    repository.vinculo_model = cast(
        type[LoteDiretoriaRegional],
        vinculo_model_mock,
    )
    diretoria_regional = DiretoriaRegional(pk=1)
    filtro_mock = vinculo_model_mock.objects.filter.return_value
    filtro_mock.values_list.return_value = [
        (123, 456),
    ]

    resultado = repository._obter_diretorias_regionais_vinculadas(
        [diretoria_regional],
    )

    assert resultado == [("123", "456")]


@pytest.mark.django_db
def test_cria_lote_e_vinculos() -> None:
    """Deve criar um lote e seus vínculos com as DREs."""
    repository = LoteRepository()
    usuario = criar_usuario_mock()
    diretoria_regional_1 = DiretoriaRegional(pk=1)
    diretoria_regional_2 = DiretoriaRegional(pk=2)
    empresa = Mock()
    lote_uuid = uuid4()

    lote_mock = Mock(spec=Lote)
    lote_mock.id = 10
    lote_mock.uuid = lote_uuid
    lote_mock.empresa = empresa
    lote_mock.diretorias_regionais = [
        diretoria_regional_1,
        diretoria_regional_2,
    ]

    model_mock = Mock(return_value=lote_mock)
    repository.model = cast(
        type[Lote],
        model_mock,
    )

    vinculo_1 = Mock(spec=LoteDiretoriaRegional)
    vinculo_2 = Mock(spec=LoteDiretoriaRegional)
    vinculo_model_mock = Mock(
        side_effect=[
            vinculo_1,
            vinculo_2,
        ],
    )
    repository.vinculo_model = cast(
        type[LoteDiretoriaRegional],
        vinculo_model_mock,
    )

    dados: dict[str, Any] = {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
        "empresa": empresa,
        "status": True,
        "diretorias_regionais": [
            diretoria_regional_1,
            diretoria_regional_2,
        ],
    }

    with patch(
        "apps.lote.repository.lote_repository.model_to_dict",
        return_value={
            "id": 10,
            "nome": "Lote Centro",
            "codigo_cadastro": "LOTE-001",
            "status": True,
        },
    ) as model_to_dict_mock:
        resultado = repository.criar(
            dados=dados,
            usuario=usuario,
        )

    model_mock.assert_called_once_with(
        nome="Lote Centro",
        codigo_cadastro="LOTE-001",
        empresa=empresa,
        status=True,
        criado_por=usuario,
        atualizado_por=usuario,
    )
    lote_mock.full_clean.assert_called_once_with()
    lote_mock.save.assert_called_once_with()

    assert vinculo_model_mock.call_count == 2
    vinculo_model_mock.assert_any_call(
        lote=lote_mock,
        diretoria_regional=diretoria_regional_1,
    )
    vinculo_model_mock.assert_any_call(
        lote=lote_mock,
        diretoria_regional=diretoria_regional_2,
    )
    vinculo_model_mock.objects.bulk_create.assert_called_once_with(
        [
            vinculo_1,
            vinculo_2,
        ]
    )
    model_to_dict_mock.assert_called_once_with(lote_mock)

    assert resultado["empresa"] is empresa
    assert resultado["diretorias_regionais"] == [
        diretoria_regional_1,
        diretoria_regional_2,
    ]
    assert resultado["uuid"] == lote_uuid
    assert resultado["pk"] == 10


@pytest.mark.django_db
def test_criar_nao_altera_dados_originais() -> None:
    """Deve preservar o dicionário recebido pelo repositório."""
    repository = LoteRepository()
    usuario = criar_usuario_mock()
    empresa = Mock()
    lote_mock = Mock(spec=Lote)
    lote_mock.id = 10
    lote_mock.uuid = uuid4()
    lote_mock.empresa = empresa
    lote_mock.diretorias_regionais = []

    model_mock = Mock(return_value=lote_mock)
    repository.model = cast(
        type[Lote],
        model_mock,
    )

    vinculo_model_mock = Mock()
    repository.vinculo_model = cast(
        type[LoteDiretoriaRegional],
        vinculo_model_mock,
    )

    dados: dict[str, Any] = {
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
        "empresa": empresa,
        "diretorias_regionais": [],
    }
    dados_originais = dados.copy()

    with patch(
        "apps.lote.repository.lote_repository.model_to_dict",
        return_value={},
    ):
        repository.criar(
            dados=dados,
            usuario=usuario,
        )

    assert dados == dados_originais
    vinculo_model_mock.objects.bulk_create.assert_called_once_with([])
