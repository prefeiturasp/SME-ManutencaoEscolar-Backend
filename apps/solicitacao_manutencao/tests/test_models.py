"""Testes dos modelos de solicitação de manutenção."""

import pytest

from apps.escola.models import Unidadeeducacional
from apps.solicitacao_manutencao.constants import SituacaoSolicitacao
from apps.solicitacao_manutencao.models import SolicitacaoManutencao

pytestmark = pytest.mark.django_db


def test_data_envio_permanece_vazia_antes_do_envio(
    unidade_educacional: Unidadeeducacional,
) -> None:
    """Mantém a data vazia enquanto a solicitação não foi enviada."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="SOL-001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )

    assert solicitacao.data_envio is None


def test_nao_preenche_data_envio_ao_alterar_situacao_diretamente(
    unidade_educacional: Unidadeeducacional,
) -> None:
    """Delega à camada de serviço o preenchimento da data de envio."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="SOL-001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )

    solicitacao.situacao = SituacaoSolicitacao.AGUARDANDO_ANALISE_DRE
    solicitacao.save(update_fields=["situacao"])
    solicitacao.refresh_from_db()

    assert solicitacao.data_envio is None
