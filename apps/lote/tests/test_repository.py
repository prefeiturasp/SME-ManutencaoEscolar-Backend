"""Testes do repositório de lotes."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock, call, patch
from uuid import uuid4

import pytest

from apps.escola.models import DiretoriaRegional
from apps.lote.models import Lote
from apps.lote.repository.lote_repository import LoteRepository
from apps.usuarios.models.usuario import Usuario

MODULO_REPOSITORY = "apps.lote.repository.lote_repository"


def test_atualiza_diretorias_regionais() -> None:
    """Deve remover vínculos antigos e criar somente os novos."""
    repository = LoteRepository()
    lote = Mock(spec=Lote)
    usuario = Mock(spec=Usuario)

    diretoria_existente = Mock(spec=DiretoriaRegional)
    diretoria_existente.pk = 1

    diretoria_nova = Mock(spec=DiretoriaRegional)
    diretoria_nova.pk = 2

    vinculo_novo = Mock()
    vinculos_atuais = Mock()
    vinculos_atuais.values_list.return_value = [1]

    with patch(
        f"{MODULO_REPOSITORY}.LoteDiretoriaRegional",
    ) as vinculo_model:
        vinculo_model.objects.filter.return_value = vinculos_atuais
        vinculo_model.return_value = vinculo_novo

        repository.atualizar_diretorias_regionais(
            lote=lote,
            diretorias_regionais=[
                diretoria_existente,
                diretoria_nova,
            ],
            usuario=usuario,
        )

    vinculo_model.objects.filter.assert_called_once_with(lote=lote)

    vinculos_atuais.exclude.assert_called_once_with(
        diretoria_regional_id__in={1, 2},
    )
    vinculos_atuais.exclude.return_value.delete.assert_called_once_with()

    vinculos_atuais.values_list.assert_called_once_with(
        "diretoria_regional_id",
        flat=True,
    )

    vinculo_model.assert_called_once_with(
        lote=lote,
        diretoria_regional=diretoria_nova,
        criado_por=usuario,
    )
    vinculo_model.objects.bulk_create.assert_called_once_with(
        [vinculo_novo],
    )


def test_obtem_diretorias_regionais_vinculadas() -> None:
    """Deve retornar as DREs vinculadas a lotes ativos."""
    repository = LoteRepository()
    vinculo_model = Mock()
    queryset = Mock()

    diretoria = Mock(spec=DiretoriaRegional)
    diretoria.pk = 4

    vinculo = SimpleNamespace(
        diretoria_regional=SimpleNamespace(
            nome_curto="DRE CAPELA DO SOCORRO",
        ),
        lote=SimpleNamespace(
            codigo_cadastro="LOTE-002",
        ),
    )

    vinculo_model.objects.filter.return_value = queryset
    queryset.select_related.return_value = [vinculo]
    repository.vinculo_model = vinculo_model

    resultado = repository._obter_diretorias_regionais_vinculadas(
        [diretoria],
    )

    vinculo_model.objects.filter.assert_called_once_with(
        diretoria_regional_id__in=[4],
        lote__status=True,
        lote__deletado_em__isnull=True,
    )
    queryset.exclude.assert_not_called()
    queryset.select_related.assert_called_once_with(
        "diretoria_regional",
        "lote",
    )

    assert resultado == [
        ("DRE CAPELA DO SOCORRO", "LOTE-002"),
    ]


def test_obtem_diretorias_desconsiderando_lote_informado() -> None:
    """Deve ignorar os vínculos pertencentes ao lote informado."""
    repository = LoteRepository()
    vinculo_model = Mock()
    queryset = Mock()
    queryset_sem_lote_ignorado = Mock()

    diretoria = Mock(spec=DiretoriaRegional)
    diretoria.pk = 4

    lote_ignorado = Mock(spec=Lote)
    lote_ignorado.pk = 10

    vinculo_model.objects.filter.return_value = queryset
    queryset.exclude.return_value = queryset_sem_lote_ignorado
    queryset_sem_lote_ignorado.select_related.return_value = []
    repository.vinculo_model = vinculo_model

    resultado = repository._obter_diretorias_regionais_vinculadas(
        [diretoria],
        lote_ignorado=lote_ignorado,
    )

    queryset.exclude.assert_called_once_with(lote_id=10)
    queryset_sem_lote_ignorado.select_related.assert_called_once_with(
        "diretoria_regional",
        "lote",
    )

    assert resultado == []


@pytest.mark.django_db
def test_cria_lote_com_diretorias_regionais() -> None:
    """Deve criar o lote e seus vínculos com as diretorias."""
    repository = LoteRepository()
    model = Mock()
    vinculo_model = Mock()

    usuario = Mock(spec=Usuario)
    empresa = Mock()

    diretoria_um = Mock(spec=DiretoriaRegional)
    diretoria_dois = Mock(spec=DiretoriaRegional)
    diretorias = [diretoria_um, diretoria_dois]

    lote = Mock(spec=Lote)
    lote.id = 1
    lote.uuid = uuid4()
    lote.empresa = empresa
    lote.diretorias_regionais = diretorias

    vinculo_um = Mock()
    vinculo_dois = Mock()

    model.return_value = lote
    vinculo_model.side_effect = [vinculo_um, vinculo_dois]

    repository.model = model
    repository.vinculo_model = vinculo_model

    dados = {
        "codigo_cadastro": "LOTE-001",
        "nome": "Lote Norte",
        "status": True,
        "empresa": empresa,
        "periodo_inicial": date(2026, 9, 1),
        "periodo_final": date(2026, 9, 30),
        "diretorias_regionais": diretorias,
    }

    dados_modelo = {
        "codigo_cadastro": "LOTE-001",
        "nome": "Lote Norte",
        "status": True,
    }

    with patch(
        f"{MODULO_REPOSITORY}.model_to_dict",
        return_value=dados_modelo.copy(),
    ) as model_to_dict:
        resultado = repository.criar(
            dados=dados,
            usuario=usuario,
        )

    model.assert_called_once_with(
        codigo_cadastro="LOTE-001",
        nome="Lote Norte",
        status=True,
        empresa=empresa,
        periodo_inicial=date(2026, 9, 1),
        periodo_final=date(2026, 9, 30),
        criado_por=usuario,
        atualizado_por=usuario,
    )

    lote.full_clean.assert_called_once_with()
    lote.save.assert_called_once_with()

    vinculo_model.assert_has_calls(
        [
            call(
                lote=lote,
                diretoria_regional=diretoria_um,
            ),
            call(
                lote=lote,
                diretoria_regional=diretoria_dois,
            ),
        ]
    )
    vinculo_model.objects.bulk_create.assert_called_once_with(
        [vinculo_um, vinculo_dois],
    )
    model_to_dict.assert_called_once_with(lote)

    assert resultado == {
        **dados_modelo,
        "empresa": empresa,
        "diretorias_regionais": diretorias,
        "uuid": lote.uuid,
        "pk": 1,
    }

    assert "diretorias_regionais" in dados


def test_atualiza_lote_com_diretorias_regionais() -> None:
    """Deve atualizar o lote e sincronizar suas diretorias."""
    repository = LoteRepository()
    lote = Mock(spec=Lote)
    usuario = Mock(spec=Usuario)
    diretoria = Mock(spec=DiretoriaRegional)

    dados = {
        "nome": "Lote atualizado",
        "status": False,
        "diretorias_regionais": [diretoria],
    }
    resultado_esperado = {
        "id": 1,
        "nome": "Lote atualizado",
        "status": False,
    }

    with (
        patch.object(
            repository,
            "atualizar_diretorias_regionais",
        ) as atualizar_diretorias,
        patch.object(
            repository,
            "_serializar",
            return_value=resultado_esperado,
        ) as serializar,
    ):
        resultado = repository.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

    assert lote.nome == "Lote atualizado"
    assert lote.status is False
    assert lote.atualizado_por is usuario

    atualizar_diretorias.assert_called_once_with(
        lote=lote,
        diretorias_regionais=[diretoria],
        usuario=usuario,
    )
    lote.full_clean.assert_called_once_with()
    assert lote.save.call_count == 2
    serializar.assert_called_once_with(lote)

    assert resultado == resultado_esperado


def test_atualiza_lote_sem_diretorias_regionais() -> None:
    """Deve atualizar o lote sem sincronizar as diretorias."""
    repository = LoteRepository()
    lote = Mock(spec=Lote)
    usuario = Mock(spec=Usuario)

    dados = {
        "nome": "Lote atualizado",
        "status": True,
    }
    resultado_esperado = {
        "id": 1,
        "nome": "Lote atualizado",
        "status": True,
    }

    with (
        patch.object(
            repository,
            "atualizar_diretorias_regionais",
        ) as atualizar_diretorias,
        patch.object(
            repository,
            "_serializar",
            return_value=resultado_esperado,
        ) as serializar,
    ):
        resultado = repository.atualizar(
            lote=lote,
            dados=dados,
            usuario=usuario,
        )

    atualizar_diretorias.assert_not_called()
    lote.full_clean.assert_called_once_with()
    assert lote.save.call_count == 2
    serializar.assert_called_once_with(lote)

    assert resultado == resultado_esperado


def test_serializa_lote() -> None:
    """Deve acrescentar o ID e o UUID aos dados serializados."""
    repository = LoteRepository()
    lote = Mock(spec=Lote)
    lote.id = 15
    lote.uuid = uuid4()

    with patch(
        f"{MODULO_REPOSITORY}.model_to_dict",
        return_value={"nome": "Lote Norte"},
    ) as model_to_dict:
        resultado = repository._serializar(lote)

    model_to_dict.assert_called_once_with(lote)

    assert resultado == {
        "nome": "Lote Norte",
        "id": 15,
        "uuid": str(lote.uuid),
    }
