"""Testes dos comandos de gerenciamento relacionados aos lotes."""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.empresa.models import Empresa
from apps.lote.models import Lote


@pytest.mark.django_db
def test_comando_inativacao_automatica_lotes_vencidos() -> None:
    """O comando inativa apenas lotes vencidos, ativos e não deletados."""
    data_atual = timezone.localdate()

    empresa = Empresa.objects.create(nome="Empresa Teste")

    lote_vencido = Lote.objects.create(
        empresa=empresa,
        nome="Lote Vencido",
        codigo_cadastro="VENC01",
        status=True,
        periodo_final=data_atual - timedelta(days=1),
        deletado_em=None,
    )

    lote_vigente = Lote.objects.create(
        empresa=empresa,
        nome="Lote Vigente",
        codigo_cadastro="VIG02",
        status=True,
        periodo_final=data_atual + timedelta(days=5),
        deletado_em=None,
    )

    lote_ja_inativo = Lote.objects.create(
        empresa=empresa,
        nome="Lote Inativo",
        codigo_cadastro="INA03",
        status=False,
        periodo_final=data_atual - timedelta(days=2),
        deletado_em=None,
    )

    resultado = call_command("inativar_lotes_expirados")

    lote_vencido.refresh_from_db()
    lote_vigente.refresh_from_db()
    lote_ja_inativo.refresh_from_db()

    assert resultado is None
    assert lote_vencido.status is False
    assert lote_vigente.status is True
    assert lote_ja_inativo.status is False
