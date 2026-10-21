"""Testes dos repositórios de solicitações de manutenção."""

import pytest

from apps.escola.models import Unidadeeducacional
from apps.solicitacao_manutencao.models import SolicitacaoManutencao
from apps.solicitacao_manutencao.repository import (
    ArquivoServicoManutencaoRepository,
    ServicoManutencaoRepository,
    SolicitacaoManutencaoRepository,
)
from apps.usuarios.models import Usuario

pytestmark = pytest.mark.django_db


def test_cria_solicitacao(
    unidade_educacional: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste uma solicitação de manutenção."""
    solicitacao = SolicitacaoManutencaoRepository().criar(
        dados={
            "codigo": "0000001",
            "tipo_atendimento": "comum",
            "unidade_educacional": unidade_educacional,
        },
        usuario=usuario_ativo,
    )

    assert solicitacao["codigo"] == "0000001"
    assert solicitacao["criado_por"] == usuario_ativo
    solicitacao_criada = SolicitacaoManutencao.objects.get(
        id=solicitacao["id"]
    )
    assert str(solicitacao_criada) == (f"0000001 - {unidade_educacional}")


def test_cria_servico_da_solicitacao(
    unidade_educacional: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste um serviço vinculado à solicitação."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )
    servico = ServicoManutencaoRepository().criar(
        dados={
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao_id=solicitacao.id,
        usuario=usuario_ativo,
    )

    assert servico["solicitacao_manutencao"] == solicitacao
    assert servico["criado_por"] == usuario_ativo
    assert (
        str(servico["solicitacao_manutencao"].servicos_manutencao.get())
        == "Reparo hidráulico - Cozinha"
    )


def test_cria_arquivo_do_servico(
    unidade_educacional: Unidadeeducacional,
    usuario_ativo: Usuario,
) -> None:
    """Persiste um arquivo vinculado ao serviço."""
    solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )
    servico = ServicoManutencaoRepository().criar(
        dados={
            "servico_especifico": "Reparo hidráulico",
            "local_reparo": "Cozinha",
            "descricao": "Vazamento na pia",
        },
        solicitacao_id=solicitacao.id,
        usuario=usuario_ativo,
    )
    arquivo = ArquivoServicoManutencaoRepository().criar(
        dados={
            "nome_original": "reparo.jpg",
            "arquivo": "arquivos/reparo.jpg",
            "tipo": "imagem",
            "tipo_mime": "image/jpeg",
            "tamanho_bytes": 16,
        },
        servico_id=servico["id"],
        usuario=usuario_ativo,
    )

    assert arquivo["servico_manutencao"].id == servico["id"]
    assert arquivo["criado_por"] == usuario_ativo


def test_obtem_ultimo_codigo_incluindo_solicitacao_excluida(
    unidade_educacional: Unidadeeducacional,
) -> None:
    """Consulta o maior código mesmo quando o registro foi excluído."""
    SolicitacaoManutencao.objects.create(
        codigo="0000001",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )
    ultima_solicitacao = SolicitacaoManutencao.objects.create(
        codigo="0000002",
        tipo_atendimento="comum",
        unidade_educacional=unidade_educacional,
    )
    ultima_solicitacao.soft_delete()

    ultimo_codigo = SolicitacaoManutencaoRepository().obter_ultimo_codigo()

    assert ultimo_codigo == {"codigo": "0000002"}


def test_obtem_ultimo_codigo_retorna_dict_vazio_sem_solicitacoes() -> None:
    """Retorna um dicionário vazio quando não houver solicitações."""
    ultimo_codigo = SolicitacaoManutencaoRepository().obter_ultimo_codigo()

    assert ultimo_codigo == {}
