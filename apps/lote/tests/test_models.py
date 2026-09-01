"""Testes dos modelos relacionados aos lotes."""

from typing import cast
from unittest.mock import Mock, patch

from django.db import models
from django.db.models import QuerySet

from apps.escola.models import DiretoriaRegional
from apps.lote.models import (
    Lote,
    LoteDiretoriaRegional,
)


def test_representacao_textual_do_lote() -> None:
    """Deve retornar o nome como representação do lote."""
    lote = Lote(
        codigo_cadastro="LOTE-001",
        nome="Lote Centro",
    )

    resultado = str(lote)

    assert resultado == "Lote Centro"


def test_status_padrao_do_lote() -> None:
    """Deve criar o lote com status ativo por padrão."""
    lote = Lote(
        codigo_cadastro="LOTE-001",
        nome="Lote Centro",
    )

    assert lote.status is True


def test_metadados_do_lote() -> None:
    """Deve configurar corretamente os metadados do lote."""
    assert Lote._meta.verbose_name == "lote"
    assert Lote._meta.verbose_name_plural == "lotes"
    assert Lote._meta.ordering == ["-status", "-id"]


def test_retorna_diretorias_regionais_vinculadas() -> None:
    """Deve retornar as Diretorias Regionais vinculadas ao lote."""
    lote = Lote(
        codigo_cadastro="LOTE-001",
        nome="Lote Centro",
    )
    queryset = cast(
        QuerySet[DiretoriaRegional],
        Mock(spec=QuerySet),
    )

    with patch.object(
        DiretoriaRegional.objects,
        "filter",
        return_value=queryset,
    ) as filter_mock:
        resultado = lote.diretorias_regionais

    assert resultado is queryset
    filter_mock.assert_called_once_with(
        vinculo_lote__lote=lote,
    )


def test_representacao_textual_do_vinculo() -> None:
    """Deve retornar o lote e a Diretoria Regional do vínculo."""
    lote = Lote(
        codigo_cadastro="LOTE-001",
        nome="Lote Centro",
    )
    diretoria_regional = DiretoriaRegional(
        nome="Diretoria Regional Centro",
    )
    vinculo = LoteDiretoriaRegional(
        lote=lote,
        diretoria_regional=diretoria_regional,
    )

    resultado = str(vinculo)

    assert resultado == (f"{lote} - {diretoria_regional}")


def test_metadados_do_vinculo() -> None:
    """Deve configurar corretamente os metadados do vínculo."""
    assert (
        LoteDiretoriaRegional._meta.verbose_name
        == "Diretoria Regional do lote"
    )
    assert (
        LoteDiretoriaRegional._meta.verbose_name_plural
        == "Diretorias Regionais do lote"
    )
    assert LoteDiretoriaRegional._meta.ordering == ["id"]


def test_relacionamento_com_lote() -> None:
    """Deve configurar o relacionamento do vínculo com o lote."""
    campo = LoteDiretoriaRegional._meta.get_field("lote")

    assert isinstance(campo, models.ForeignKey)
    assert campo.remote_field is not None
    assert campo.remote_field.model is Lote
    assert campo.remote_field.on_delete is models.CASCADE
    assert campo.remote_field.related_name == "vinculos_diretoria_regional"


def test_relacionamento_exclusivo_com_diretoria_regional() -> None:
    """Deve configurar uma Diretoria Regional por vínculo."""
    campo = LoteDiretoriaRegional._meta.get_field(
        "diretoria_regional",
    )

    assert isinstance(campo, models.ForeignKey)
    assert campo.remote_field is not None
    assert campo.remote_field.model is DiretoriaRegional
    assert campo.remote_field.on_delete is models.PROTECT
    assert campo.remote_field.related_name == "vinculo_lote"
