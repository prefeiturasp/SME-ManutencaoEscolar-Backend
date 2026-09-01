"""Testes do repositório de lotes."""

from typing import Any, cast
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote, LoteDiretoriaRegional
from apps.lote.repository.lote_repository import LoteRepository
from apps.usuarios.models.usuario import Usuario


def criar_usuario_mock() -> Usuario:
    """Cria um usuário simulado para os testes."""
    return cast(Usuario, Mock(spec=Usuario))


def criar_vinculo_mock(
    nome_dre: str,
    codigo_lote: str,
) -> LoteDiretoriaRegional:
    """Cria um vínculo simulado entre uma DRE e um lote.

    Args:
        nome_dre: Nome curto da diretoria regional.
        codigo_lote: Código de cadastro do lote.

    Returns:
        Vínculo simulado contendo uma diretoria regional e um lote.
    """
    diretoria_regional = Mock(spec=DiretoriaRegional)
    diretoria_regional.nome_curto = nome_dre

    lote = Mock(spec=Lote)
    lote.codigo_cadastro = codigo_lote

    vinculo = Mock(spec=LoteDiretoriaRegional)
    vinculo.diretoria_regional = diretoria_regional
    vinculo.lote = lote

    return cast(LoteDiretoriaRegional, vinculo)


def test_obtem_diretorias_regionais_vinculadas() -> None:
    """Deve retornar os nomes das DREs e os códigos dos lotes."""
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
        criar_vinculo_mock(
            nome_dre="Centro",
            codigo_lote="LOTE-001",
        ),
        criar_vinculo_mock(
            nome_dre="Norte",
            codigo_lote="LOTE-002",
        ),
    ]

    filtro_mock = vinculo_model_mock.objects.filter.return_value
    filtro_mock.select_related.return_value = vinculos

    resultado = repository._obter_diretorias_regionais_vinculadas(
        diretorias_regionais,
    )

    assert resultado == [
        ("Centro", "LOTE-001"),
        ("Norte", "LOTE-002"),
    ]

    vinculo_model_mock.objects.filter.assert_called_once_with(
        diretoria_regional_id__in=[1, 2],
        lote__status=True,
    )
    filtro_mock.select_related.assert_called_once_with(
        "diretoria_regional",
        "lote",
    )


def test_obtem_lista_vazia_quando_nao_existem_vinculos() -> None:
    """Deve retornar uma lista vazia quando não existem vínculos."""
    repository = LoteRepository()
    vinculo_model_mock = Mock()

    repository.vinculo_model = cast(
        type[LoteDiretoriaRegional],
        vinculo_model_mock,
    )

    filtro_mock = vinculo_model_mock.objects.filter.return_value
    filtro_mock.select_related.return_value = []

    resultado = repository._obter_diretorias_regionais_vinculadas([])

    assert resultado == []

    vinculo_model_mock.objects.filter.assert_called_once_with(
        diretoria_regional_id__in=[],
        lote__status=True,
    )
    filtro_mock.select_related.assert_called_once_with(
        "diretoria_regional",
        "lote",
    )


@pytest.mark.django_db
def test_cria_lote_e_vinculos() -> None:
    """Deve criar um lote e seus vínculos com as DREs."""
    repository = LoteRepository()
    usuario = criar_usuario_mock()
    empresa = Mock()

    diretoria_regional_1 = DiretoriaRegional(pk=1)
    diretoria_regional_2 = DiretoriaRegional(pk=2)

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

    assert resultado == {
        "id": 10,
        "nome": "Lote Centro",
        "codigo_cadastro": "LOTE-001",
        "status": True,
        "empresa": empresa,
        "diretorias_regionais": [
            diretoria_regional_1,
            diretoria_regional_2,
        ],
        "uuid": lote_uuid,
        "pk": 10,
    }


@pytest.mark.django_db
def test_cria_lote_sem_diretorias_regionais() -> None:
    """Deve criar um lote sem vínculos quando nenhuma DRE é informada."""
    repository = LoteRepository()
    usuario = criar_usuario_mock()
    empresa = Mock()

    lote_uuid = uuid4()
    lote_mock = Mock(spec=Lote)
    lote_mock.id = 10
    lote_mock.uuid = lote_uuid
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
    }

    with patch(
        "apps.lote.repository.lote_repository.model_to_dict",
        return_value={},
    ):
        resultado = repository.criar(
            dados=dados,
            usuario=usuario,
        )

    model_mock.assert_called_once_with(
        nome="Lote Centro",
        codigo_cadastro="LOTE-001",
        empresa=empresa,
        criado_por=usuario,
        atualizado_por=usuario,
    )

    vinculo_model_mock.assert_not_called()
    vinculo_model_mock.objects.bulk_create.assert_called_once_with([])

    assert resultado["diretorias_regionais"] == []
    assert resultado["empresa"] is empresa
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


@pytest.mark.django_db
def test_criar_propaga_erro_de_validacao() -> None:
    """Deve propagar o erro quando o lote não passa pela validação."""
    repository = LoteRepository()
    usuario = criar_usuario_mock()

    lote_mock = Mock(spec=Lote)
    lote_mock.full_clean.side_effect = ValidationError(
        "Dados inválidos.",
    )

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
        "nome": "",
        "codigo_cadastro": "LOTE-001",
        "diretorias_regionais": [],
    }

    with pytest.raises(
        ValidationError,
        match="Dados inválidos",
    ):
        repository.criar(
            dados=dados,
            usuario=usuario,
        )

    lote_mock.full_clean.assert_called_once_with()
    lote_mock.save.assert_not_called()
    vinculo_model_mock.objects.bulk_create.assert_not_called()
